"""
Confidence Validator: Hybrid Confidence Assessment

This module provides optional semantic validation of routing decisions
using vector embeddings. It does NOT replace the deterministic routing,
but rather provides an additional confidence signal.

Key Responsibilities:
1. Calculate semantic similarity between query and section
2. Validate that deterministic routing aligns with semantic similarity
3. Boost or reduce confidence based on semantic agreement
4. Detect potential routing errors (high keyword score, low semantic score)

Design Philosophy:
- Primary routing: Deterministic (TF-IDF + metadata)
- Confidence boost: Semantic similarity (optional)
- Result: Explainable + validated
"""

from typing import Optional, Tuple, Dict
import os


class ConfidenceValidator:
    """
    Optional semantic validation for routing confidence.
    
    This class provides a hybrid approach:
    1. Deterministic routing (TF-IDF) makes the decision
    2. Semantic similarity (embeddings) validates the decision
    3. Combined confidence reflects both signals
    
    Benefits:
    - Maintains explainability (TF-IDF is primary)
    - Adds semantic validation (catches edge cases)
    - Improves confidence calibration
    - Optional (can disable for compliance-critical deployments)
    """
    
    def __init__(self, enable_semantic: bool = False):
        """
        Initialize the confidence validator.
        
        Args:
            enable_semantic: Whether to enable semantic validation
                            (requires sentence-transformers library)
        """
        self.enable_semantic = enable_semantic
        self.model = None
        
        if enable_semantic:
            try:
                from sentence_transformers import SentenceTransformer
                # Use a lightweight, fast model
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                print("Warning: sentence-transformers not installed. Semantic validation disabled.")
                print("Install with: pip install sentence-transformers")
                self.enable_semantic = False
    
    def validate_routing(
        self,
        query: str,
        section_text: str,
        deterministic_score: float,
        section_label: str = ""
    ) -> Tuple[float, Dict]:
        """
        Validate routing decision and calculate combined confidence.
        
        This combines:
        1. Deterministic score (TF-IDF + metadata) - PRIMARY
        2. Semantic similarity (optional) - VALIDATION
        
        Args:
            query: The user's question
            section_text: The text of the matched section
            deterministic_score: Score from TF-IDF routing
            section_label: Optional label for logging
        
        Returns:
            Tuple of (combined_confidence: float, metadata: Dict)
        """
        # Normalize deterministic score to 0-1 range
        deterministic_confidence = min(1.0, deterministic_score / 100.0)
        
        metadata = {
            'deterministic_confidence': deterministic_confidence,
            'semantic_similarity': None,
            'agreement': None,
            'validation_enabled': self.enable_semantic
        }
        
        if not self.enable_semantic or self.model is None:
            # No semantic validation - return deterministic confidence
            return deterministic_confidence, metadata
        
        # Calculate semantic similarity
        semantic_similarity = self._calculate_similarity(query, section_text)
        metadata['semantic_similarity'] = semantic_similarity
        
        # Check agreement between deterministic and semantic scores
        agreement = self._calculate_agreement(
            deterministic_confidence,
            semantic_similarity
        )
        metadata['agreement'] = agreement
        
        # Combine scores based on agreement
        combined_confidence = self._combine_scores(
            deterministic_confidence,
            semantic_similarity,
            agreement
        )
        
        return combined_confidence, metadata
    
    def _calculate_similarity(self, query: str, text: str) -> float:
        """
        Calculate semantic similarity using embeddings.
        
        Args:
            query: The query text
            text: The section text
        
        Returns:
            Similarity score (0-1)
        """
        if self.model is None:
            return 0.0
        
        try:
            # Encode both texts
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            text_embedding = self.model.encode(text[:512], convert_to_tensor=True)  # Limit text length
            
            # Calculate cosine similarity
            from sentence_transformers import util
            similarity = util.cos_sim(query_embedding, text_embedding).item()
            
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            print(f"Warning: Semantic similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_agreement(
        self,
        deterministic: float,
        semantic: float
    ) -> str:
        """
        Calculate agreement level between deterministic and semantic scores.
        
        Args:
            deterministic: Deterministic confidence (0-1)
            semantic: Semantic similarity (0-1)
        
        Returns:
            Agreement level: 'high', 'medium', 'low', or 'conflict'
        """
        diff = abs(deterministic - semantic)
        
        if diff < 0.15:
            return 'high'  # Scores agree strongly
        elif diff < 0.30:
            return 'medium'  # Scores somewhat agree
        elif deterministic > 0.5 and semantic < 0.3:
            return 'conflict'  # High keyword match, low semantic (potential issue)
        elif semantic > 0.5 and deterministic < 0.3:
            return 'conflict'  # High semantic, low keyword (rare edge case)
        else:
            return 'low'  # Scores disagree
    
    def _combine_scores(
        self,
        deterministic: float,
        semantic: float,
        agreement: str
    ) -> float:
        """
        Combine deterministic and semantic scores based on agreement.
        
        Strategy:
        - High agreement: Boost confidence slightly
        - Medium agreement: Use deterministic score
        - Low agreement: Reduce confidence slightly
        - Conflict: Significantly reduce confidence (potential routing error)
        
        Args:
            deterministic: Deterministic confidence (0-1)
            semantic: Semantic similarity (0-1)
            agreement: Agreement level
        
        Returns:
            Combined confidence (0-1)
        """
        if agreement == 'high':
            # Both signals agree - boost confidence
            # Weighted average: 70% deterministic, 30% semantic
            combined = deterministic * 0.7 + semantic * 0.3
            # Add small boost for agreement
            return min(1.0, combined * 1.1)
        
        elif agreement == 'medium':
            # Moderate agreement - use deterministic with slight semantic influence
            return deterministic * 0.8 + semantic * 0.2
        
        elif agreement == 'conflict':
            # Conflict detected - significantly reduce confidence
            # This flags potential routing errors
            return min(deterministic, semantic) * 0.6
        
        else:  # low agreement
            # Disagreement - reduce confidence moderately
            return deterministic * 0.85
    
    def get_validation_summary(self) -> str:
        """
        Get a summary of the validation configuration.
        
        Returns:
            Human-readable summary
        """
        if not self.enable_semantic:
            return "Semantic validation: DISABLED (deterministic routing only)"
        
        if self.model is None:
            return "Semantic validation: ENABLED but model failed to load"
        
        return f"Semantic validation: ENABLED (model: {self.model._modules['0'].auto_model.name_or_path})"


def create_confidence_validator(enable_semantic: Optional[bool] = None) -> ConfidenceValidator:
    """
    Factory function to create a confidence validator.
    
    Args:
        enable_semantic: Whether to enable semantic validation.
                        If None, reads from ENABLE_SEMANTIC_VALIDATION env var.
    
    Returns:
        ConfidenceValidator instance
    """
    if enable_semantic is None:
        # Check environment variable
        enable_semantic = os.getenv('ENABLE_SEMANTIC_VALIDATION', 'false').lower() == 'true'
    
    return ConfidenceValidator(enable_semantic=enable_semantic)
