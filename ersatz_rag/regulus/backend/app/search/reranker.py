"""
Cross-Encoder Reranker - Final relevance refinement component

This implements cross-encoder reranking as part of the hybrid search engine.
Provides final relevance scoring to optimize precision of search results.
"""

import logging
from typing import List, Tuple, Dict, Any
import numpy as np
from dataclasses import dataclass

# Import for sentence transformers cross-encoder (if available)
try:
    from sentence_transformers import CrossEncoder
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logging.warning("sentence-transformers not available, using fallback reranker")

logger = logging.getLogger(__name__)

@dataclass
class RerankResult:
    """Result from reranking operation"""
    query: str
    document: str
    relevance_score: float
    rank: int

class CrossEncoderReranker:
    """
    Cross-encoder based reranking for final relevance refinement
    
    Uses a cross-encoder model to score query-document pairs for precise
    relevance assessment. Falls back to heuristic scoring if model unavailable.
    """
    
    def __init__(self, 
                 model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
                 use_heuristic_fallback: bool = True):
        """
        Initialize cross-encoder reranker
        
        Args:
            model_name: HuggingFace model name for cross-encoder
            use_heuristic_fallback: Use heuristic scoring if model unavailable
        """
        
        self.model_name = model_name
        self.use_heuristic_fallback = use_heuristic_fallback
        self.model = None
        
        # Initialize model if available
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = CrossEncoder(model_name)
                logger.info(f"✅ Cross-encoder reranker loaded: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load cross-encoder model: {e}")
                if not use_heuristic_fallback:
                    raise
        
        # Heuristic scoring patterns for corporate policy documents
        self.relevance_patterns = {
            'exact_match': 3.0,      # Exact phrase matches
            'title_match': 2.5,      # Matches in section titles
            'policy_terms': 2.0,     # Policy-specific terminology
            'proximity': 1.5,        # Query terms in proximity
            'partial_match': 1.0,    # Partial term matches
            'semantic_related': 0.5  # Semantically related terms
        }
        
        self.policy_keywords = {
            'governance', 'compliance', 'policy', 'procedure', 'guideline',
            'requirement', 'mandatory', 'authorization', 'approval', 'review',
            'artificial intelligence', 'machine learning', 'ai', 'ml', 'algorithm'
        }
        
        logger.info(f"🎯 Reranker initialized (fallback: {use_heuristic_fallback})")
    
    def rerank(self, query_doc_pairs: List[Tuple[str, str]]) -> List[float]:
        """
        Rerank query-document pairs for relevance
        
        Args:
            query_doc_pairs: List of (query, document) tuples to score
            
        Returns:
            List of relevance scores (0-1 range) for each pair
        """
        
        if not query_doc_pairs:
            return []
        
        logger.debug(f"🎯 Reranking {len(query_doc_pairs)} query-document pairs")
        
        if self.model:
            return self._model_rerank(query_doc_pairs)
        elif self.use_heuristic_fallback:
            return self._heuristic_rerank(query_doc_pairs)
        else:
            # Return uniform scores if no method available
            logger.warning("No reranking method available, returning uniform scores")
            return [0.5] * len(query_doc_pairs)
    
    def _model_rerank(self, query_doc_pairs: List[Tuple[str, str]]) -> List[float]:
        """Rerank using cross-encoder model"""
        
        try:
            # Get cross-encoder scores
            scores = self.model.predict(query_doc_pairs)
            
            # Convert to list and normalize to 0-1 range
            if isinstance(scores, np.ndarray):
                scores = scores.tolist()
            
            # Apply sigmoid to convert logits to probabilities
            normalized_scores = [self._sigmoid(score) for score in scores]
            
            logger.debug(f"✅ Model reranking completed, avg score: {np.mean(normalized_scores):.3f}")
            return normalized_scores
            
        except Exception as e:
            logger.error(f"Model reranking failed: {e}")
            if self.use_heuristic_fallback:
                return self._heuristic_rerank(query_doc_pairs)
            else:
                return [0.5] * len(query_doc_pairs)
    
    def _heuristic_rerank(self, query_doc_pairs: List[Tuple[str, str]]) -> List[float]:
        """
        Heuristic reranking based on text analysis patterns
        
        Implements rule-based relevance scoring optimized for corporate policy documents.
        """
        
        logger.debug("Using heuristic reranking")
        
        scores = []
        for query, document in query_doc_pairs:
            score = self._calculate_heuristic_score(query, document)
            scores.append(score)
        
        # Normalize scores to 0-1 range
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            if max_score > min_score:
                normalized_scores = [(s - min_score) / (max_score - min_score) for s in scores]
            else:
                normalized_scores = [0.5] * len(scores)  # All equal scores
        else:
            normalized_scores = []
        
        logger.debug(f"✅ Heuristic reranking completed, avg score: {np.mean(normalized_scores):.3f}")
        return normalized_scores
    
    def _calculate_heuristic_score(self, query: str, document: str) -> float:
        """
        Calculate heuristic relevance score based on text analysis
        """
        
        query_lower = query.lower()
        doc_lower = document.lower()
        query_terms = query_lower.split()
        
        total_score = 0.0
        
        # 1. Exact phrase match (highest priority)
        if query_lower in doc_lower:
            total_score += self.relevance_patterns['exact_match']
        
        # 2. Title/header match (check first 100 chars for titles)
        doc_start = doc_lower[:100]
        for term in query_terms:
            if term in doc_start:
                total_score += self.relevance_patterns['title_match']
        
        # 3. Policy-specific terminology boost
        policy_matches = sum(1 for keyword in self.policy_keywords 
                           if keyword in query_lower and keyword in doc_lower)
        total_score += policy_matches * self.relevance_patterns['policy_terms']
        
        # 4. Term proximity analysis
        proximity_score = self._calculate_proximity_score(query_terms, doc_lower)
        total_score += proximity_score * self.relevance_patterns['proximity']
        
        # 5. Partial term matching
        partial_matches = 0
        for query_term in query_terms:
            if len(query_term) >= 3:  # Only for terms of reasonable length
                for word in doc_lower.split():
                    if query_term in word or word in query_term:
                        partial_matches += 1
                        break
        total_score += partial_matches * self.relevance_patterns['partial_match']
        
        # 6. Document length penalty (prefer more concise, focused content)
        doc_length = len(document.split())
        if doc_length > 500:  # Penalty for very long documents
            total_score *= 0.9
        elif doc_length < 50:  # Penalty for very short documents
            total_score *= 0.8
        
        return total_score
    
    def _calculate_proximity_score(self, query_terms: List[str], document: str) -> float:
        """
        Calculate score based on proximity of query terms in document
        """
        
        words = document.split()
        word_positions = {}
        
        # Find positions of query terms
        for i, word in enumerate(words):
            for term in query_terms:
                if term in word.lower():
                    if term not in word_positions:
                        word_positions[term] = []
                    word_positions[term].append(i)
        
        if len(word_positions) < 2:
            return 0.0
        
        # Calculate minimum distance between any two query terms
        min_distance = float('inf')
        terms_with_positions = list(word_positions.items())
        
        for i in range(len(terms_with_positions)):
            for j in range(i + 1, len(terms_with_positions)):
                term1_positions = terms_with_positions[i][1]
                term2_positions = terms_with_positions[j][1]
                
                for pos1 in term1_positions:
                    for pos2 in term2_positions:
                        distance = abs(pos1 - pos2)
                        min_distance = min(min_distance, distance)
        
        # Convert distance to proximity score (closer = higher score)
        if min_distance == float('inf'):
            return 0.0
        
        # Exponential decay: score decreases as distance increases
        proximity_score = max(0, 1.0 - (min_distance / 20.0))  # Full score if within 20 words
        return proximity_score
    
    def _sigmoid(self, x: float) -> float:
        """Apply sigmoid function to convert logits to probabilities"""
        try:
            return 1.0 / (1.0 + np.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0
    
    def rank_results(self, query: str, documents: List[str]) -> List[RerankResult]:
        """
        Rank documents for a query and return detailed results
        
        Args:
            query: Search query
            documents: List of document texts to rank
            
        Returns:
            List of RerankResult objects sorted by relevance
        """
        
        if not documents:
            return []
        
        # Create query-document pairs
        query_doc_pairs = [(query, doc) for doc in documents]
        
        # Get relevance scores
        scores = self.rerank(query_doc_pairs)
        
        # Create results with ranks
        results = []
        score_doc_pairs = list(zip(scores, documents))
        score_doc_pairs.sort(key=lambda x: x[0], reverse=True)
        
        for rank, (score, document) in enumerate(score_doc_pairs):
            results.append(RerankResult(
                query=query,
                document=document,
                relevance_score=score,
                rank=rank + 1
            ))
        
        return results
    
    def explain_score(self, query: str, document: str) -> Dict[str, Any]:
        """
        Explain how a relevance score was calculated (for heuristic method)
        """
        
        if self.model and not self.use_heuristic_fallback:
            return {
                'method': 'model',
                'model_name': self.model_name,
                'explanation': 'Score computed by cross-encoder neural model'
            }
        
        query_lower = query.lower()
        doc_lower = document.lower()
        query_terms = query_lower.split()
        
        explanation = {
            'method': 'heuristic',
            'query': query,
            'query_terms': query_terms,
            'scoring_factors': {}
        }
        
        # Analyze each scoring factor
        factors = explanation['scoring_factors']
        
        # Exact match
        factors['exact_match'] = {
            'found': query_lower in doc_lower,
            'weight': self.relevance_patterns['exact_match']
        }
        
        # Policy terms
        policy_matches = [keyword for keyword in self.policy_keywords 
                         if keyword in query_lower and keyword in doc_lower]
        factors['policy_terms'] = {
            'matches': policy_matches,
            'count': len(policy_matches),
            'weight_per_match': self.relevance_patterns['policy_terms']
        }
        
        # Proximity
        proximity_score = self._calculate_proximity_score(query_terms, doc_lower)
        factors['proximity'] = {
            'score': proximity_score,
            'weight': self.relevance_patterns['proximity']
        }
        
        # Document length
        doc_length = len(document.split())
        length_penalty = 0.9 if doc_length > 500 else (0.8 if doc_length < 50 else 1.0)
        factors['document_length'] = {
            'word_count': doc_length,
            'penalty_multiplier': length_penalty
        }
        
        return explanation
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the reranker model and configuration"""
        
        return {
            'model_loaded': self.model is not None,
            'model_name': self.model_name,
            'has_sentence_transformers': HAS_SENTENCE_TRANSFORMERS,
            'fallback_enabled': self.use_heuristic_fallback,
            'relevance_patterns': self.relevance_patterns,
            'policy_keywords_count': len(self.policy_keywords)
        }