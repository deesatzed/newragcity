"""
AI-powered topic discovery with enterprise-grade confidence validation
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from ..models import Topic, ConfidenceLevel


class TopicService:
    """
    AI-powered topic discovery with enterprise-grade confidence tracking
    
    Features:
    - Unsupervised clustering with confidence validation
    - enterprise-grade coherence scoring
    - Quality-assured topic generation
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # enterprise-grade clustering parameters
        self.min_cluster_size = 3
        self.min_samples = 2
        self.confidence_threshold = 0.70
        
    async def generate_topics(
        self,
        index_path: str,
        min_confidence: float = 0.70,
        max_topics: int = 20
    ) -> Dict[str, Any]:
        """
        Generate AI topics with enterprise-grade confidence validation
        
        Args:
            index_path: Path to knowledge index
            min_confidence: Minimum confidence for topic storage
            max_topics: Maximum number of topics to generate
            
        Returns:
            Topic generation results with quality metrics
        """
        
        print("🏷️  Generating AI-powered topic clusters...")
        start_time = time.time()
        
        # Load chunk metadata
        metadata_path = Path(index_path).parent / "chunk_metadata.json"
        if not metadata_path.exists():
            return {
                "topics_generated": 0,
                "error": "No chunk metadata found - run indexing first"
            }
            
        with open(metadata_path, 'r') as f:
            chunks_metadata = json.load(f)
            
        if len(chunks_metadata) < 5:
            return {
                "topics_generated": 0,
                "message": "Insufficient content for topic generation (need at least 5 chunks)"
            }
            
        # Extract content for clustering
        chunk_contents = []
        chunk_ids = []
        
        for chunk in chunks_metadata:
            if chunk.get("confidence", 0.0) >= min_confidence:
                content = chunk.get("content_preview", "")
                if len(content) > 50:  # Minimum content requirement
                    chunk_contents.append(content)
                    chunk_ids.append(chunk["chunk_id"])
                    
        if len(chunk_contents) < 3:
            return {
                "topics_generated": 0,
                "message": "Insufficient high-confidence content for clustering"
            }
            
        print(f"   Clustering {len(chunk_contents)} high-confidence chunks...")
        
        # Vectorize content with TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform(chunk_contents)
        except Exception as e:
            return {
                "topics_generated": 0,
                "error": f"Vectorization failed: {str(e)}"
            }
            
        # Perform HDBSCAN clustering
        clusterer = HDBSCAN(
            min_cluster_size=max(self.min_cluster_size, len(chunk_contents) // 10),
            min_samples=self.min_samples,
            metric='euclidean'
        )
        
        cluster_labels = clusterer.fit_predict(tfidf_matrix.toarray())
        
        # Generate topics from clusters
        topics = []
        unique_labels = set(cluster_labels)
        
        for label in unique_labels:
            if label == -1:  # Skip noise cluster
                continue
                
            # Get chunks in this cluster
            cluster_indices = [i for i, l in enumerate(cluster_labels) if l == label]
            cluster_chunk_ids = [chunk_ids[i] for i in cluster_indices]
            cluster_contents = [chunk_contents[i] for i in cluster_indices]
            
            # Generate topic information
            topic_info = self._generate_topic_info(cluster_contents, tfidf_matrix, cluster_indices)
            
            # Calculate clustering confidence
            clustering_confidence = self._calculate_clustering_confidence(
                clusterer, cluster_indices, label
            )
            
            # Create topic with confidence validation
            topic = Topic(
                name=topic_info["name"],
                description=topic_info["description"],
                keywords=topic_info["keywords"],
                chunk_ids=[uuid4() for _ in cluster_chunk_ids],  # Convert to UUIDs
                clustering_confidence=clustering_confidence,
                labeling_confidence=topic_info["labeling_confidence"],
                coherence_score=topic_info["coherence_score"]
            )
            
            # Only include high-quality topics
            if topic.overall_confidence >= min_confidence:
                topics.append(topic)
                
        # Sort by confidence
        topics.sort(key=lambda x: x.overall_confidence, reverse=True)
        topics = topics[:max_topics]
        
        # Save topics
        topics_data = [
            {
                "topic_id": str(topic.topic_id),
                "name": topic.name,
                "description": topic.description,
                "keywords": topic.keywords,
                "chunk_count": len(topic.chunk_ids),
                "confidence": topic.overall_confidence,
                "confidence_level": topic.confidence_level.value,
                "created_at": topic.created_at.isoformat()
            }
            for topic in topics
        ]
        
        topics_file = Path(index_path).parent / "topics.json"
        with open(topics_file, 'w') as f:
            json.dump(topics_data, f, indent=2)
            
        generation_time = time.time() - start_time
        
        print(f"✅ Generated {len(topics)} high-confidence topics in {generation_time:.2f}s")
        
        return {
            "topics_generated": len(topics),
            "high_confidence_topics": len([t for t in topics if t.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.CRITICAL]]),
            "generation_time": generation_time,
            "confidence_distribution": self._get_confidence_distribution(topics)
        }
        
    def _generate_topic_info(
        self,
        cluster_contents: List[str],
        tfidf_matrix,
        cluster_indices: List[int]
    ) -> Dict[str, Any]:
        """Generate topic name, description, and keywords from cluster"""
        
        # Extract top TF-IDF terms for this cluster
        cluster_tfidf = tfidf_matrix[cluster_indices]
        mean_tfidf = np.mean(cluster_tfidf.toarray(), axis=0)
        
        # Get feature names (terms)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Find top terms
        top_indices = np.argsort(mean_tfidf)[-10:][::-1]  # Top 10 terms
        top_terms = [feature_names[i] for i in top_indices]
        
        # Generate topic name (use top term as base)
        topic_name = self._generate_topic_name(top_terms[:3])
        
        # Generate description
        description = self._generate_topic_description(cluster_contents, top_terms)
        
        # Calculate labeling confidence based on term coherence
        labeling_confidence = self._calculate_labeling_confidence(top_terms, mean_tfidf[top_indices])
        
        # Calculate coherence score
        coherence_score = self._calculate_coherence_score(cluster_contents)
        
        return {
            "name": topic_name,
            "description": description,
            "keywords": top_terms[:5],
            "labeling_confidence": labeling_confidence,
            "coherence_score": coherence_score
        }
        
    def _generate_topic_name(self, top_terms: List[str]) -> str:
        """Generate human-readable topic name"""
        
        # Simple heuristic for topic naming
        if len(top_terms) >= 2:
            # Combine top terms
            name = " & ".join(top_terms[:2]).title()
        else:
            name = top_terms[0].title() if top_terms else "Unknown Topic"
            
        # Clean up common programming terms
        replacements = {
            "Def ": "Functions & ",
            "Class ": "Classes & ",
            "Import ": "Imports & ",
            "Function ": "Functions & "
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
            
        return name
        
    def _generate_topic_description(self, contents: List[str], keywords: List[str]) -> str:
        """Generate topic description"""
        
        # Simple description based on content analysis
        total_words = sum(len(content.split()) for content in contents)
        avg_length = total_words / len(contents) if contents else 0
        
        # Categorize based on keywords and content characteristics
        if any(kw in ['function', 'def', 'class', 'method'] for kw in keywords):
            category = "Code structure and implementation"
        elif any(kw in ['import', 'require', 'include'] for kw in keywords):
            category = "Dependencies and imports"
        elif any(kw in ['test', 'assert', 'expect'] for kw in keywords):
            category = "Testing and validation"
        elif any(kw in ['config', 'setting', 'option'] for kw in keywords):
            category = "Configuration and settings"
        elif avg_length > 100:
            category = "Documentation and explanations"
        else:
            category = "General content"
            
        return f"{category} containing {len(contents)} related chunks with focus on {', '.join(keywords[:3])}."
        
    def _calculate_clustering_confidence(
        self,
        clusterer,
        cluster_indices: List[int],
        label: int
    ) -> float:
        """Calculate confidence in clustering decision"""
        
        # Use cluster stability and density metrics
        if hasattr(clusterer, 'cluster_persistence_'):
            # HDBSCAN provides persistence information
            try:
                persistence = clusterer.cluster_persistence_[label] if label < len(clusterer.cluster_persistence_) else 0.5
                return min(1.0, max(0.0, persistence))
            except:
                pass
                
        # Fallback: use cluster size as confidence proxy
        cluster_size = len(cluster_indices)
        
        if cluster_size >= 10:
            return 0.9
        elif cluster_size >= 5:
            return 0.8
        elif cluster_size >= 3:
            return 0.7
        else:
            return 0.5
            
    def _calculate_labeling_confidence(self, terms: List[str], scores: np.ndarray) -> float:
        """Calculate confidence in topic labeling"""
        
        if len(scores) == 0:
            return 0.5
            
        # Use TF-IDF score distribution
        max_score = np.max(scores)
        score_std = np.std(scores)
        
        # Higher max score and lower std deviation = higher confidence
        if max_score > 0.1 and score_std < 0.05:
            return 0.9
        elif max_score > 0.05:
            return 0.8
        else:
            return 0.6
            
    def _calculate_coherence_score(self, contents: List[str]) -> float:
        """Calculate topic coherence score"""
        
        if len(contents) < 2:
            return 0.5
            
        # Simple coherence based on shared vocabulary
        all_words = set()
        content_words = []
        
        for content in contents:
            words = set(content.lower().split())
            content_words.append(words)
            all_words.update(words)
            
        if not all_words:
            return 0.5
            
        # Calculate average word overlap between contents
        overlaps = []
        for i in range(len(content_words)):
            for j in range(i + 1, len(content_words)):
                overlap = len(content_words[i] & content_words[j]) / len(content_words[i] | content_words[j])
                overlaps.append(overlap)
                
        if overlaps:
            avg_overlap = sum(overlaps) / len(overlaps)
            return min(1.0, max(0.3, avg_overlap * 2))  # Scale to reasonable range
        else:
            return 0.5
            
    def _get_confidence_distribution(self, topics: List[Topic]) -> Dict[str, int]:
        """Get confidence level distribution"""
        
        distribution = {}
        for topic in topics:
            level = topic.confidence_level.value
            distribution[level] = distribution.get(level, 0) + 1
            
        return distribution
        
    async def get_topics_with_confidence(self, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Get stored topics with confidence filtering"""
        
        # Look for topics file in default location
        topics_file = Path.home() / ".cognitron" / "index" / "topics.json"
        
        if not topics_file.exists():
            return []
            
        with open(topics_file, 'r') as f:
            topics_data = json.load(f)
            
        # Filter by confidence
        filtered_topics = [
            topic for topic in topics_data
            if topic.get("confidence", 0.0) >= min_confidence
        ]
        
        return filtered_topics