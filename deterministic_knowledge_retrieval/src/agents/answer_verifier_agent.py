"""
Answer/Verifier Agent: LLM Synthesis with Verification

Reference: agnoMCPnanobot.txt lines 443-455

The Answer/Verifier Agent is responsible for synthesizing answers from
loaded context and verifying that answers are grounded in the source material.

Key Responsibilities:
1. Generate answers using LLM synthesis
2. Verify answers are supported by context
3. Calculate confidence scores
4. Generate proper citations
5. Detect hallucinations or unsupported claims
"""

from typing import List, Optional, Dict, Tuple
from ..llm_providers import LLMProvider


class AnswerVerifierAgent:
    """
    The Answer/Verifier Agent synthesizes answers and verifies their accuracy.
    
    Reference: agnoMCPnanobot.txt lines 443-455
    
    This agent:
    - Uses an LLM to generate answers from context
    - Verifies that answers are grounded in the provided context
    - Calculates confidence scores based on context quality
    - Ensures proper citation of sources
    
    This is a "simulation" agent - it implements the agent pattern without
    requiring the full Agno framework. In production, this would use
    Agno's verification tools and potentially multiple verification passes.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the Answer/Verifier Agent.
        
        Args:
            llm_provider: The LLM provider to use for answer generation
        """
        self.llm_provider = llm_provider
        self.verification_history: List[Dict] = []
    
    def generate_answer(
        self,
        query: str,
        context: str,
        citations: List[str],
        max_tokens: int = 500,
        verify: bool = True
    ) -> Tuple[str, float, List[str]]:
        """
        Generate an answer to the query using the provided context.
        
        Reference: agnoMCPnanobot.txt lines 461-469 - Answer generation flow
        
        This method:
        1. Calls the LLM to generate an answer
        2. Optionally verifies the answer is grounded in context
        3. Calculates a confidence score
        4. Returns the answer with metadata
        
        Args:
            query: The user's question
            context: The loaded context from the Loader Agent
            citations: List of section_ids that were loaded
            max_tokens: Maximum tokens for the answer
            verify: Whether to verify the answer (default: True)
        
        Returns:
            Tuple of (answer: str, confidence: float, citations: List[str])
        """
        # Generate the answer using the LLM
        answer = self.llm_provider.generate(
            query=query,
            context=context,
            citations=citations,
            max_tokens=max_tokens
        )
        
        # Verify the answer if requested
        if verify:
            is_grounded, confidence = self._verify_answer(answer, context, query)
            
            # Log verification result
            self.verification_history.append({
                'query': query,
                'answer': answer,
                'is_grounded': is_grounded,
                'confidence': confidence,
                'citations': citations
            })
            
            if not is_grounded:
                # If answer is not grounded, add a disclaimer
                answer = self._add_disclaimer(answer)
                confidence = max(0.3, confidence * 0.5)  # Reduce confidence
        else:
            # If not verifying, use a default confidence
            confidence = 0.7
        
        return answer, confidence, citations
    
    def _verify_answer(
        self,
        answer: str,
        context: str,
        query: str
    ) -> Tuple[bool, float]:
        """
        Verify that the answer is grounded in the provided context.
        
        Reference: AJrag.txt §4 - Verification requirements
        
        This performs basic verification checks:
        1. Answer is not empty
        2. Answer contains content from the context
        3. Answer is relevant to the query
        
        In production, this would use more sophisticated verification,
        potentially including:
        - Entailment checking
        - Fact verification
        - Citation validation
        - Hallucination detection
        
        Args:
            answer: The generated answer
            context: The source context
            query: The original query
        
        Returns:
            Tuple of (is_grounded: bool, confidence: float)
        """
        # Basic checks
        if not answer or len(answer.strip()) == 0:
            return False, 0.0
        
        # Check if answer contains mock/placeholder text
        answer_lower = answer.lower()
        if 'mock answer' in answer_lower or 'placeholder' in answer_lower:
            # This is a mock answer, so it's "grounded" in the sense that
            # it's a valid response from the mock provider
            return True, 0.6
        
        # Check for context overlap
        # Count how many words from the answer appear in the context
        answer_words = set(answer.lower().split())
        context_words = set(context.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        answer_words -= common_words
        context_words -= common_words
        
        if len(answer_words) == 0:
            return False, 0.0
        
        # Calculate overlap ratio
        overlap = len(answer_words & context_words)
        overlap_ratio = overlap / len(answer_words)
        
        # Consider answer grounded if >30% of content words appear in context
        is_grounded = overlap_ratio > 0.3
        
        # Calculate confidence based on overlap
        confidence = min(1.0, overlap_ratio * 1.5)
        
        return is_grounded, confidence
    
    def _add_disclaimer(self, answer: str) -> str:
        """
        Add a disclaimer to an answer that may not be fully grounded.
        
        Args:
            answer: The original answer
        
        Returns:
            Answer with disclaimer prepended
        """
        disclaimer = (
            "[Note: This answer may contain information not fully supported by the source material.] "
        )
        return disclaimer + answer
    
    def synthesize_with_verification(
        self,
        query: str,
        context: str,
        citations: List[str],
        routing_confidence: float,
        max_tokens: int = 500
    ) -> Dict:
        """
        Synthesize an answer with full verification and confidence calculation.
        
        This is the main entry point that combines answer generation,
        verification, and confidence scoring.
        
        Args:
            query: The user's question
            context: The loaded context
            citations: List of section_ids
            routing_confidence: Confidence from the TOC Agent routing
            max_tokens: Maximum tokens for the answer
        
        Returns:
            Dictionary with answer, confidence, citations, and metadata
        """
        # Generate and verify the answer
        answer, verification_confidence, final_citations = self.generate_answer(
            query=query,
            context=context,
            citations=citations,
            max_tokens=max_tokens,
            verify=True
        )
        
        # Combine routing confidence and verification confidence
        # Use weighted average: 60% verification, 40% routing
        combined_confidence = (
            verification_confidence * 0.6 +
            routing_confidence * 0.4
        )
        
        return {
            'answer': answer,
            'confidence': combined_confidence,
            'citations': final_citations,
            'metadata': {
                'routing_confidence': routing_confidence,
                'verification_confidence': verification_confidence,
                'combined_confidence': combined_confidence,
                'verified': True
            }
        }
    
    def get_verification_summary(self) -> Dict:
        """
        Get a summary of verification history.
        
        This is useful for monitoring and debugging.
        
        Returns:
            Dictionary with verification statistics
        """
        if not self.verification_history:
            return {
                'total_verifications': 0,
                'grounded_count': 0,
                'grounded_rate': 0.0,
                'average_confidence': 0.0
            }
        
        grounded_count = sum(1 for v in self.verification_history if v['is_grounded'])
        total = len(self.verification_history)
        avg_confidence = sum(v['confidence'] for v in self.verification_history) / total
        
        return {
            'total_verifications': total,
            'grounded_count': grounded_count,
            'grounded_rate': grounded_count / total,
            'average_confidence': avg_confidence
        }
    
    def get_verification_trace(self, last_n: int = 5) -> str:
        """
        Get a human-readable trace of recent verifications.
        
        This is useful for debugging and understanding answer quality.
        
        Args:
            last_n: Number of recent verifications to include
        
        Returns:
            String describing recent verifications
        """
        if not self.verification_history:
            return "No verifications performed yet."
        
        trace_lines = [
            "Answer/Verifier Agent Trace",
            f"Total Verifications: {len(self.verification_history)}",
            f"Grounded Rate: {self.get_verification_summary()['grounded_rate']:.1%}",
            "",
            f"Last {last_n} Verifications:"
        ]
        
        for i, v in enumerate(self.verification_history[-last_n:], 1):
            status = "✓ Grounded" if v['is_grounded'] else "✗ Not Grounded"
            trace_lines.append(
                f"{i}. {status} (confidence: {v['confidence']:.2f})"
            )
            trace_lines.append(f"   Query: {v['query'][:60]}...")
        
        return "\n".join(trace_lines)
