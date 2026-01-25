"""
Hybrid Search Engine - Combines semantic, lexical, and reranking approaches

This implements the hybrid search strategy from Phase 1 Week 1-2 of the build checklist:
- Semantic search via LEANN + Granite embeddings (existing)
- BM25 lexical search for keyword matching
- Cross-encoder reranking for relevance refinement
- Query expansion and reformulation

Target: 15-25% accuracy improvement over semantic-only search
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import math
import re

from leann.api import LeannSearcher
from .bm25_searcher import BM25Searcher
from .reranker import CrossEncoderReranker

logger = logging.getLogger(__name__)

@dataclass
class HybridSearchResult:
    """Enhanced search result with multiple scoring factors"""
    content: str
    metadata: Dict[str, Any]
    semantic_score: float
    lexical_score: float
    rerank_score: Optional[float]
    hybrid_score: float
    node_id: str
    source_info: Dict[str, Any]

class HybridSearchEngine:
    """
    Revolutionary hybrid search combining semantic + lexical + reranking
    
    This is the foundation for the 25% accuracy improvement target in Phase 1.
    Integrates with the existing three-approach RAG system (PageIndex + LEANN + deepConf).
    """
    
    def __init__(self, 
                 leann_index_path: str,
                 embedding_model: str = "ibm-granite/granite-embedding-english-r2",
                 semantic_weight: float = 0.5,
                 lexical_weight: float = 0.3,
                 rerank_weight: float = 0.2):
        """
        Initialize hybrid search with configurable scoring weights
        
        Args:
            leann_index_path: Path to existing LEANN index
            embedding_model: Granite embedding model for semantic search
            semantic_weight: Weight for semantic similarity scores  
            lexical_weight: Weight for BM25 lexical scores
            rerank_weight: Weight for cross-encoder reranking scores
        """
        
        self.embedding_model = embedding_model
        self.weights = {
            'semantic': semantic_weight,
            'lexical': lexical_weight,
            'rerank': rerank_weight
        }
        
        # Initialize semantic search (existing LEANN + Granite)
        try:
            self.semantic_searcher = LeannSearcher(leann_index_path)
            logger.info(f"✅ Semantic search initialized with {embedding_model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize semantic search: {e}")
            raise
        
        # Initialize BM25 lexical search
        self.lexical_searcher = BM25Searcher()
        
        # Initialize cross-encoder reranker
        self.reranker = CrossEncoderReranker()
        
        # Query enhancement patterns
        self.query_patterns = {
            'policy_terms': ['policy', 'procedure', 'guideline', 'compliance', 'requirement'],
            'ai_terms': ['artificial intelligence', 'AI', 'machine learning', 'ML', 'algorithm'],
            'governance_terms': ['governance', 'oversight', 'approval', 'authorization', 'review']
        }
        
        logger.info(f"🔍 Hybrid Search Engine initialized")
        logger.info(f"   Semantic weight: {semantic_weight}")
        logger.info(f"   Lexical weight: {lexical_weight}")  
        logger.info(f"   Rerank weight: {rerank_weight}")
    
    def search(self, 
              query: str, 
              top_k: int = 10,
              enable_reranking: bool = True,
              enable_query_expansion: bool = True) -> List[HybridSearchResult]:
        """
        Execute hybrid search with semantic + lexical + reranking
        
        Args:
            query: User query string
            top_k: Number of results to return
            enable_reranking: Whether to apply cross-encoder reranking
            enable_query_expansion: Whether to expand query with related terms
            
        Returns:
            List of HybridSearchResult objects ranked by hybrid score
        """
        
        logger.info(f"🔍 Executing hybrid search: '{query}'")
        
        # Step 1: Query expansion and reformulation
        if enable_query_expansion:
            expanded_query = self._expand_query(query)
            logger.debug(f"Query expanded: '{query}' -> '{expanded_query}'")
        else:
            expanded_query = query
        
        # Step 2: Parallel semantic and lexical search
        semantic_results = self._semantic_search(expanded_query, top_k=top_k*2)
        lexical_results = self._lexical_search(expanded_query, top_k=top_k*2) 
        
        logger.debug(f"Retrieved {len(semantic_results)} semantic, {len(lexical_results)} lexical results")
        
        # Step 3: Combine and deduplicate results
        combined_results = self._combine_results(semantic_results, lexical_results)
        
        # Step 4: Calculate hybrid scores
        hybrid_results = self._calculate_hybrid_scores(combined_results, query)
        
        # Step 5: Apply cross-encoder reranking (optional)
        if enable_reranking and len(hybrid_results) > 1:
            hybrid_results = self._apply_reranking(hybrid_results, query)
        
        # Step 6: Final ranking and top-k selection
        final_results = sorted(hybrid_results, key=lambda x: x.hybrid_score, reverse=True)[:top_k]
        
        logger.info(f"✅ Hybrid search completed: {len(final_results)} results")
        self._log_score_distribution(final_results)
        
        return final_results
    
    def _expand_query(self, query: str) -> str:
        """
        Expand query with related terms for better coverage
        
        This implements query expansion from the build checklist to improve
        recall by adding domain-specific synonyms and related terms.
        """
        
        query_lower = query.lower()
        expansions = []
        
        # Add domain-specific expansions
        for domain, terms in self.query_patterns.items():
            if any(term.lower() in query_lower for term in terms):
                # Add related terms from the same domain
                related_terms = [t for t in terms if t.lower() not in query_lower]
                expansions.extend(related_terms[:2])  # Limit to avoid query bloat
        
        # Add synonyms for common policy terms
        synonyms_map = {
            'policy': ['guideline', 'procedure'],
            'ai': ['artificial intelligence', 'machine learning'],
            'approval': ['authorization', 'permission'],
            'compliance': ['adherence', 'conformance']
        }
        
        for word in query_lower.split():
            if word in synonyms_map:
                expansions.extend(synonyms_map[word][:1])
        
        if expansions:
            expanded = f"{query} {' '.join(expansions)}"
            return expanded
        
        return query
    
    def _semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Execute semantic search via existing LEANN + Granite embeddings"""
        
        try:
            results = self.semantic_searcher.search(query, top_k=top_k)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result.text,
                    'metadata': dict(result.metadata),
                    'score': result.score,
                    'node_id': result.metadata.get('node_id', 'unknown'),
                    'search_type': 'semantic'
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    def _lexical_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Execute BM25 lexical search for keyword matching"""
        
        try:
            # Build or refresh BM25 index from LEANN data if needed
            if not self.lexical_searcher.is_ready():
                self._build_bm25_index()
            
            results = self.lexical_searcher.search(query, top_k=top_k)
            return results
            
        except Exception as e:
            logger.error(f"Lexical search error: {e}")
            return []
    
    def _build_bm25_index(self):
        """Build BM25 index from existing LEANN data"""
        
        logger.info("🔨 Building BM25 lexical index from LEANN data...")
        
        try:
            # Extract all documents from LEANN searcher for BM25 indexing
            # This is a simplified approach - in production, would maintain parallel indices
            documents = []
            
            # Query with broad terms to get corpus for BM25
            broad_queries = ['policy', 'AI', 'governance', 'compliance', 'procedure']
            
            for broad_query in broad_queries:
                results = self.semantic_searcher.search(broad_query, top_k=50)
                for result in results:
                    doc_info = {
                        'content': result.text,
                        'metadata': dict(result.metadata),
                        'node_id': result.metadata.get('node_id', 'unknown')
                    }
                    if doc_info not in documents:  # Simple deduplication
                        documents.append(doc_info)
            
            # Build BM25 index
            self.lexical_searcher.build_index(documents)
            logger.info(f"✅ BM25 index built with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to build BM25 index: {e}")
            raise
    
    def _combine_results(self, semantic_results: List[Dict], lexical_results: List[Dict]) -> List[Dict]:
        """
        Combine and deduplicate results from semantic and lexical search
        
        Uses node_id for deduplication and merges scores appropriately.
        """
        
        # Use node_id as deduplication key
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            node_id = result['node_id']
            combined[node_id] = {
                **result,
                'semantic_score': result['score'],
                'lexical_score': 0.0,  # Will be updated if found in lexical results
                'found_in_semantic': True,
                'found_in_lexical': False
            }
        
        # Merge lexical results
        for result in lexical_results:
            node_id = result['node_id']
            if node_id in combined:
                # Update existing result with lexical score
                combined[node_id]['lexical_score'] = result['score']
                combined[node_id]['found_in_lexical'] = True
            else:
                # Add new result found only in lexical search
                combined[node_id] = {
                    **result,
                    'semantic_score': 0.0,
                    'lexical_score': result['score'],
                    'found_in_semantic': False,
                    'found_in_lexical': True
                }
        
        return list(combined.values())
    
    def _calculate_hybrid_scores(self, combined_results: List[Dict], query: str) -> List[HybridSearchResult]:
        """
        Calculate hybrid scores using weighted combination of semantic + lexical scores
        """
        
        hybrid_results = []
        
        # Normalize scores to 0-1 range for fair combination
        semantic_scores = [r['semantic_score'] for r in combined_results if r['semantic_score'] > 0]
        lexical_scores = [r['lexical_score'] for r in combined_results if r['lexical_score'] > 0]
        
        semantic_max = max(semantic_scores) if semantic_scores else 1.0
        lexical_max = max(lexical_scores) if lexical_scores else 1.0
        
        for result in combined_results:
            # Normalize individual scores
            norm_semantic = result['semantic_score'] / semantic_max if semantic_max > 0 else 0
            norm_lexical = result['lexical_score'] / lexical_max if lexical_max > 0 else 0
            
            # Calculate hybrid score
            hybrid_score = (
                norm_semantic * self.weights['semantic'] +
                norm_lexical * self.weights['lexical']
            )
            
            # Boost score if found in both search methods (intersection bonus)
            if result['found_in_semantic'] and result['found_in_lexical']:
                hybrid_score *= 1.2  # 20% boost for intersection
            
            # Create hybrid result object
            hybrid_result = HybridSearchResult(
                content=result['content'],
                metadata=result['metadata'],
                semantic_score=norm_semantic,
                lexical_score=norm_lexical,
                rerank_score=None,  # Will be set by reranker
                hybrid_score=hybrid_score,
                node_id=result['node_id'],
                source_info={
                    'found_in_semantic': result['found_in_semantic'],
                    'found_in_lexical': result['found_in_lexical'],
                    'raw_semantic_score': result['semantic_score'],
                    'raw_lexical_score': result['lexical_score']
                }
            )
            
            hybrid_results.append(hybrid_result)
        
        return hybrid_results
    
    def _apply_reranking(self, results: List[HybridSearchResult], query: str) -> List[HybridSearchResult]:
        """
        Apply cross-encoder reranking for final relevance refinement
        
        This implements the reranking component from the build checklist
        to improve precision of the final results.
        """
        
        try:
            logger.debug(f"🎯 Applying cross-encoder reranking to {len(results)} results")
            
            # Prepare query-document pairs for reranking
            query_doc_pairs = [(query, result.content) for result in results]
            
            # Get reranking scores
            rerank_scores = self.reranker.rerank(query_doc_pairs)
            
            # Update results with reranking scores and recalculate hybrid scores
            for i, result in enumerate(results):
                result.rerank_score = rerank_scores[i]
                
                # Recalculate hybrid score with reranking component
                result.hybrid_score = (
                    result.semantic_score * self.weights['semantic'] +
                    result.lexical_score * self.weights['lexical'] +
                    result.rerank_score * self.weights['rerank']
                )
                
                # Keep intersection bonus
                if result.source_info['found_in_semantic'] and result.source_info['found_in_lexical']:
                    result.hybrid_score *= 1.2
            
            logger.debug("✅ Reranking completed")
            return results
            
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Return original results if reranking fails
            return results
    
    def _log_score_distribution(self, results: List[HybridSearchResult]):
        """Log score distribution for monitoring and debugging"""
        
        if not results:
            return
        
        semantic_avg = sum(r.semantic_score for r in results) / len(results)
        lexical_avg = sum(r.lexical_score for r in results) / len(results)
        hybrid_avg = sum(r.hybrid_score for r in results) / len(results)
        
        intersection_count = sum(1 for r in results 
                                if r.source_info['found_in_semantic'] and r.source_info['found_in_lexical'])
        
        logger.debug(f"Score distribution - Semantic avg: {semantic_avg:.3f}, "
                    f"Lexical avg: {lexical_avg:.3f}, Hybrid avg: {hybrid_avg:.3f}")
        logger.debug(f"Intersection results: {intersection_count}/{len(results)} "
                    f"({100*intersection_count/len(results):.1f}%)")
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get hybrid search engine statistics"""
        
        return {
            'engine_type': 'hybrid',
            'components': {
                'semantic': {
                    'model': self.embedding_model,
                    'weight': self.weights['semantic']
                },
                'lexical': {
                    'algorithm': 'BM25',
                    'weight': self.weights['lexical']
                },
                'reranker': {
                    'model': self.reranker.model_name if hasattr(self.reranker, 'model_name') else 'cross-encoder',
                    'weight': self.weights['rerank']
                }
            },
            'features': [
                'query_expansion',
                'intersection_boosting', 
                'cross_encoder_reranking',
                'multi_score_fusion'
            ]
        }

    def update_weights(self, semantic: float, lexical: float, rerank: float):
        """Update scoring weights for experimentation and optimization"""
        
        total = semantic + lexical + rerank
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.weights = {
            'semantic': semantic,
            'lexical': lexical, 
            'rerank': rerank
        }
        
        logger.info(f"Updated hybrid search weights: {self.weights}")