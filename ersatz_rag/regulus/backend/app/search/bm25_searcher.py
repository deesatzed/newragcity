"""
BM25 Lexical Searcher - Traditional keyword-based search component

This implements the BM25 algorithm for lexical search as part of the hybrid
search engine. Provides keyword-based retrieval to complement semantic search.
"""

import logging
import math
import re
from typing import List, Dict, Any, Set
from collections import defaultdict, Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BM25Document:
    """Document representation for BM25 indexing"""
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    terms: List[str]
    term_count: int

class BM25Searcher:
    """
    BM25 (Best Matching 25) implementation for lexical search
    
    Provides keyword-based retrieval using the probabilistic BM25 ranking function.
    Optimized for corporate policy documents with domain-specific term processing.
    """
    
    def __init__(self, k1: float = 1.2, b: float = 0.75):
        """
        Initialize BM25 searcher with tunable parameters
        
        Args:
            k1: Controls non-linear term frequency normalization (1.2-2.0 typical)
            b: Controls document length normalization (0.0-1.0, 0.75 typical)
        """
        
        self.k1 = k1
        self.b = b
        
        # Index structures
        self.documents: Dict[str, BM25Document] = {}
        self.inverted_index: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.doc_frequencies: Dict[str, int] = defaultdict(int)
        
        # Corpus statistics
        self.corpus_size = 0
        self.avg_doc_length = 0.0
        self.total_doc_length = 0
        
        # Preprocessing patterns
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'this', 'that',
            'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
            'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves'
        }
        
        # Domain-specific term preservation (don't filter these)
        self.preserve_terms = {
            'ai', 'ml', 'api', 'ui', 'ux', 'id', 'ip', 'it', 'hr', 'ceo', 'cto',
            'gdpr', 'hipaa', 'sox', 'iso', 'nist', 'pci', 'dss'
        }
        
        self._ready = False
        
        logger.info(f"🔤 BM25Searcher initialized (k1={k1}, b={b})")
    
    def is_ready(self) -> bool:
        """Check if BM25 index is ready for searching"""
        return self._ready
    
    def build_index(self, documents: List[Dict[str, Any]]):
        """
        Build BM25 inverted index from document collection
        
        Args:
            documents: List of document dictionaries with 'content', 'metadata', 'node_id'
        """
        
        logger.info(f"🔨 Building BM25 index from {len(documents)} documents")
        
        self._reset_index()
        
        for doc_data in documents:
            doc_id = doc_data['node_id']
            content = doc_data['content']
            metadata = doc_data['metadata']
            
            # Preprocess and tokenize content
            terms = self._preprocess_text(content)
            
            # Create document object
            document = BM25Document(
                doc_id=doc_id,
                content=content,
                metadata=metadata,
                terms=terms,
                term_count=len(terms)
            )
            
            self.documents[doc_id] = document
            self.total_doc_length += len(terms)
            
            # Build inverted index
            term_counts = Counter(terms)
            for term, count in term_counts.items():
                self.inverted_index[term][doc_id] = count
                if doc_id not in [doc for doc in self.inverted_index[term] if doc != doc_id]:
                    self.doc_frequencies[term] += 1
        
        # Calculate corpus statistics
        self.corpus_size = len(self.documents)
        self.avg_doc_length = self.total_doc_length / self.corpus_size if self.corpus_size > 0 else 0
        
        self._ready = True
        
        logger.info(f"✅ BM25 index built: {self.corpus_size} docs, {len(self.inverted_index)} terms, "
                   f"avg doc length: {self.avg_doc_length:.1f}")
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search using BM25 ranking
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of search results with BM25 scores
        """
        
        if not self._ready:
            logger.warning("BM25 index not ready, returning empty results")
            return []
        
        logger.debug(f"🔍 BM25 search: '{query}'")
        
        # Preprocess query
        query_terms = self._preprocess_text(query)
        
        if not query_terms:
            return []
        
        # Calculate BM25 scores for all documents
        doc_scores = defaultdict(float)
        
        for term in query_terms:
            if term in self.inverted_index:
                # Calculate IDF for this term
                df = self.doc_frequencies[term]  # Document frequency
                idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5))
                
                # Calculate BM25 contribution for each document containing this term
                for doc_id, tf in self.inverted_index[term].items():
                    doc = self.documents[doc_id]
                    
                    # BM25 term score
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc.term_count / self.avg_doc_length))
                    
                    term_score = idf * (numerator / denominator)
                    doc_scores[doc_id] += term_score
        
        # Sort by score and return top-k
        ranked_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in ranked_results[:top_k]:
            doc = self.documents[doc_id]
            results.append({
                'content': doc.content,
                'metadata': doc.metadata,
                'score': score,
                'node_id': doc_id,
                'search_type': 'lexical',
                'matched_terms': [term for term in query_terms if term in self.inverted_index and doc_id in self.inverted_index[term]]
            })
        
        logger.debug(f"✅ BM25 search completed: {len(results)} results")
        return results
    
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text for BM25 indexing and searching
        
        Applies tokenization, normalization, and stop word filtering
        optimized for corporate policy documents.
        """
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but preserve domain-specific terms
        # Keep alphanumeric, spaces, hyphens, and dots for terms like "AI-driven" or "v2.0"
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Tokenize on whitespace and common delimiters
        tokens = re.split(r'\s+|[-]+', text)
        
        # Filter and normalize tokens
        filtered_tokens = []
        for token in tokens:
            token = token.strip('.-_')  # Remove leading/trailing punctuation
            
            if token and len(token) >= 2:  # Minimum token length
                # Preserve important domain terms
                if token in self.preserve_terms:
                    filtered_tokens.append(token)
                # Filter common stop words (except preserved terms)
                elif token not in self.stop_words:
                    filtered_tokens.append(token)
        
        return filtered_tokens
    
    def _reset_index(self):
        """Reset all index structures"""
        self.documents.clear()
        self.inverted_index.clear()
        self.doc_frequencies.clear()
        self.corpus_size = 0
        self.avg_doc_length = 0.0
        self.total_doc_length = 0
        self._ready = False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get BM25 index statistics"""
        
        if not self._ready:
            return {'status': 'not_ready'}
        
        # Calculate vocabulary statistics
        vocab_size = len(self.inverted_index)
        total_postings = sum(len(postings) for postings in self.inverted_index.values())
        
        # Find most common terms
        term_freqs = [(term, len(postings)) for term, postings in self.inverted_index.items()]
        most_common_terms = sorted(term_freqs, key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'status': 'ready',
            'corpus_size': self.corpus_size,
            'vocabulary_size': vocab_size,
            'total_postings': total_postings,
            'avg_doc_length': round(self.avg_doc_length, 1),
            'total_doc_length': self.total_doc_length,
            'parameters': {'k1': self.k1, 'b': self.b},
            'most_common_terms': most_common_terms[:5],  # Top 5 for brevity
            'stop_words_count': len(self.stop_words),
            'preserved_terms_count': len(self.preserve_terms)
        }
    
    def explain_query(self, query: str) -> Dict[str, Any]:
        """
        Explain how a query would be processed by BM25
        
        Useful for debugging and transparency in search results.
        """
        
        query_terms = self._preprocess_text(query)
        
        term_explanations = []
        for term in query_terms:
            if term in self.inverted_index:
                df = self.doc_frequencies[term]
                idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5))
                
                term_explanations.append({
                    'term': term,
                    'document_frequency': df,
                    'idf_score': round(idf, 3),
                    'total_occurrences': sum(self.inverted_index[term].values()),
                    'appears_in_docs': len(self.inverted_index[term])
                })
            else:
                term_explanations.append({
                    'term': term,
                    'document_frequency': 0,
                    'idf_score': 0.0,
                    'total_occurrences': 0,
                    'appears_in_docs': 0,
                    'note': 'Term not found in index'
                })
        
        return {
            'original_query': query,
            'processed_terms': query_terms,
            'term_explanations': term_explanations,
            'filtered_stop_words': [word for word in query.lower().split() 
                                   if word in self.stop_words and word not in self.preserve_terms]
        }
    
    def tune_parameters(self, k1: float, b: float):
        """
        Update BM25 parameters for experimentation
        
        Note: Requires rebuilding index if documents are already indexed.
        """
        self.k1 = k1
        self.b = b
        logger.info(f"Updated BM25 parameters: k1={k1}, b={b}")
    
    def add_preserve_terms(self, terms: Set[str]):
        """Add domain-specific terms to preserve during preprocessing"""
        self.preserve_terms.update(term.lower() for term in terms)
        logger.info(f"Added {len(terms)} preserve terms: {terms}")
    
    def add_stop_words(self, words: Set[str]):
        """Add custom stop words for filtering"""
        self.stop_words.update(word.lower() for word in words)
        logger.info(f"Added {len(words)} stop words: {words}")