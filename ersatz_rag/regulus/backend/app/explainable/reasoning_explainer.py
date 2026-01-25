"""
Regulus Explainable AI Module
Provides comprehensive AI explainability with confidence score explanations,
source selection reasoning, and user comprehension optimization.
Target: 80% user comprehension
"""

import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import re

logger = logging.getLogger(__name__)


class ExplanationType(Enum):
    """Types of explanations the system can generate"""
    CONFIDENCE_EXPLANATION = "confidence_explanation"
    SOURCE_SELECTION = "source_selection"
    REASONING_CHAIN = "reasoning_chain"
    UNCERTAINTY_ANALYSIS = "uncertainty_analysis"
    DECISION_RATIONALE = "decision_rationale"
    LIMITATION_DISCLOSURE = "limitation_disclosure"
    ALTERNATIVE_PERSPECTIVES = "alternative_perspectives"


class ExplanationComplexity(Enum):
    """Complexity levels for explanations"""
    SIMPLE = "simple"        # Basic explanations for general users
    INTERMEDIATE = "intermediate"  # Moderate detail for informed users
    TECHNICAL = "technical"  # Detailed explanations for experts
    ADAPTIVE = "adaptive"    # Adjust complexity based on user feedback


class UserPersona(Enum):
    """User personas for tailored explanations"""
    GENERAL_PUBLIC = "general_public"
    BUSINESS_USER = "business_user"
    TECHNICAL_USER = "technical_user"
    DOMAIN_EXPERT = "domain_expert"
    AUDITOR = "auditor"
    RESEARCHER = "researcher"


@dataclass
class SourceExplanation:
    """Explanation for why specific sources were selected"""
    source_id: str
    source_title: str
    relevance_score: float
    relevance_reasons: List[str]
    credibility_score: float
    credibility_factors: List[str]
    contribution_to_answer: str
    alternative_sources: List[str]
    limitations: List[str]


@dataclass
class ConfidenceExplanation:
    """Detailed explanation of confidence scores"""
    overall_confidence: float
    confidence_factors: Dict[str, float]
    uncertainty_sources: List[str]
    confidence_calibration: Dict[str, Any]
    historical_accuracy: Optional[float]
    domain_specific_confidence: Dict[str, float]
    explanation_text: str


@dataclass
class ReasoningChainExplanation:
    """Explanation of the reasoning process"""
    chain_id: str
    steps: List[Dict[str, Any]]
    logical_connections: List[Dict[str, Any]]
    key_insights: List[str]
    alternative_reasoning_paths: List[Dict[str, Any]]
    reasoning_quality_score: float
    explanation_narrative: str


@dataclass
class ExplanationResponse:
    """Complete explanation response tailored to user needs"""
    explanation_id: str
    explanation_type: ExplanationType
    complexity_level: ExplanationComplexity
    user_persona: UserPersona
    main_explanation: str
    detailed_breakdown: Dict[str, Any]
    confidence_level: float
    comprehension_score: float
    follow_up_questions: List[str]
    related_explanations: List[str]
    visualization_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ReasoningExplainer:
    """
    Comprehensive explainable AI system providing clear, understandable
    explanations of AI reasoning processes. Target: 80% user comprehension.
    """
    
    def __init__(self):
        self.explanation_templates = self._load_explanation_templates()
        self.user_comprehension_data = {}
        self.explanation_effectiveness = {}
        self.logger = logging.getLogger(f"{__name__}.ReasoningExplainer")
        
    def explain_confidence_score(
        self,
        confidence_score: float,
        confidence_factors: Dict[str, float],
        context: Dict[str, Any],
        user_persona: UserPersona = UserPersona.GENERAL_PUBLIC,
        complexity: ExplanationComplexity = ExplanationComplexity.ADAPTIVE
    ) -> ConfidenceExplanation:
        """
        Generate comprehensive explanation of confidence score
        
        Args:
            confidence_score: Overall confidence score (0-1)
            confidence_factors: Breakdown of confidence contributors
            context: Additional context about the query and response
            user_persona: Target user type for explanation
            complexity: Desired complexity level
            
        Returns:
            Detailed confidence explanation
        """
        # Analyze confidence factors
        uncertainty_sources = self._identify_uncertainty_sources(confidence_factors)
        
        # Get historical calibration data
        confidence_calibration = self._get_confidence_calibration(confidence_score, context)
        
        # Calculate domain-specific confidence
        domain_specific_confidence = self._calculate_domain_confidence(
            confidence_factors, context
        )
        
        # Generate explanation text
        explanation_text = self._generate_confidence_explanation_text(
            confidence_score, confidence_factors, uncertainty_sources,
            user_persona, complexity
        )
        
        return ConfidenceExplanation(
            overall_confidence=confidence_score,
            confidence_factors=confidence_factors,
            uncertainty_sources=uncertainty_sources,
            confidence_calibration=confidence_calibration,
            historical_accuracy=confidence_calibration.get("historical_accuracy"),
            domain_specific_confidence=domain_specific_confidence,
            explanation_text=explanation_text
        )
    
    def explain_source_selection(
        self,
        selected_sources: List[Dict[str, Any]],
        available_sources: List[Dict[str, Any]],
        query_context: Dict[str, Any],
        user_persona: UserPersona = UserPersona.GENERAL_PUBLIC
    ) -> List[SourceExplanation]:
        """
        Explain why specific sources were selected for the answer
        
        Args:
            selected_sources: Sources used in the answer
            available_sources: All available sources
            query_context: Context of the original query
            user_persona: Target user type
            
        Returns:
            List of source explanations
        """
        explanations = []
        
        for source in selected_sources:
            # Calculate relevance and credibility
            relevance_score = self._calculate_source_relevance(source, query_context)
            credibility_score = self._calculate_source_credibility(source)
            
            # Generate relevance reasons
            relevance_reasons = self._generate_relevance_reasons(
                source, query_context, relevance_score
            )
            
            # Generate credibility factors
            credibility_factors = self._generate_credibility_factors(
                source, credibility_score
            )
            
            # Identify alternative sources
            alternative_sources = self._identify_alternative_sources(
                source, available_sources, query_context
            )
            
            # Identify limitations
            limitations = self._identify_source_limitations(source)
            
            # Generate contribution explanation
            contribution = self._explain_source_contribution(source, query_context)
            
            explanation = SourceExplanation(
                source_id=source.get("id", "unknown"),
                source_title=source.get("title", "Untitled Source"),
                relevance_score=relevance_score,
                relevance_reasons=relevance_reasons,
                credibility_score=credibility_score,
                credibility_factors=credibility_factors,
                contribution_to_answer=contribution,
                alternative_sources=alternative_sources,
                limitations=limitations
            )
            
            explanations.append(explanation)
        
        return explanations
    
    def explain_reasoning_chain(
        self,
        reasoning_steps: List[Dict[str, Any]],
        query: str,
        final_answer: str,
        user_persona: UserPersona = UserPersona.GENERAL_PUBLIC,
        complexity: ExplanationComplexity = ExplanationComplexity.ADAPTIVE
    ) -> ReasoningChainExplanation:
        """
        Generate explanation of the complete reasoning chain
        
        Args:
            reasoning_steps: List of reasoning steps taken
            query: Original query
            final_answer: Generated answer
            user_persona: Target user type
            complexity: Desired complexity level
            
        Returns:
            Complete reasoning chain explanation
        """
        chain_id = str(uuid.uuid4())
        
        # Process and simplify reasoning steps based on complexity
        processed_steps = self._process_reasoning_steps(
            reasoning_steps, complexity, user_persona
        )
        
        # Identify logical connections between steps
        logical_connections = self._identify_logical_connections(reasoning_steps)
        
        # Extract key insights
        key_insights = self._extract_key_insights(reasoning_steps, final_answer)
        
        # Generate alternative reasoning paths
        alternative_paths = self._generate_alternative_reasoning_paths(
            reasoning_steps, query, complexity
        )
        
        # Calculate reasoning quality score
        quality_score = self._calculate_reasoning_quality_score(reasoning_steps)
        
        # Generate narrative explanation
        narrative = self._generate_reasoning_narrative(
            processed_steps, key_insights, user_persona, complexity
        )
        
        return ReasoningChainExplanation(
            chain_id=chain_id,
            steps=processed_steps,
            logical_connections=logical_connections,
            key_insights=key_insights,
            alternative_reasoning_paths=alternative_paths,
            reasoning_quality_score=quality_score,
            explanation_narrative=narrative
        )
    
    def generate_comprehensive_explanation(
        self,
        query: str,
        answer: str,
        confidence_data: Dict[str, Any],
        reasoning_data: Dict[str, Any],
        sources_data: List[Dict[str, Any]],
        user_persona: UserPersona = UserPersona.GENERAL_PUBLIC,
        complexity: ExplanationComplexity = ExplanationComplexity.ADAPTIVE,
        explanation_types: List[ExplanationType] = None
    ) -> ExplanationResponse:
        """
        Generate a comprehensive explanation combining all aspects
        
        Args:
            query: Original user query
            answer: Generated answer
            confidence_data: Confidence information
            reasoning_data: Reasoning process data
            sources_data: Source information
            user_persona: Target user type
            complexity: Complexity level
            explanation_types: Specific explanation types to include
            
        Returns:
            Complete explanation response
        """
        if explanation_types is None:
            explanation_types = [
                ExplanationType.CONFIDENCE_EXPLANATION,
                ExplanationType.SOURCE_SELECTION,
                ExplanationType.REASONING_CHAIN
            ]
        
        explanation_id = str(uuid.uuid4())
        detailed_breakdown = {}
        
        # Generate confidence explanation
        if ExplanationType.CONFIDENCE_EXPLANATION in explanation_types:
            confidence_explanation = self.explain_confidence_score(
                confidence_data.get("overall_confidence", 0.0),
                confidence_data.get("factors", {}),
                {"query": query, "answer": answer},
                user_persona, complexity
            )
            detailed_breakdown["confidence"] = asdict(confidence_explanation)
        
        # Generate source explanation
        if ExplanationType.SOURCE_SELECTION in explanation_types and sources_data:
            source_explanations = self.explain_source_selection(
                sources_data, sources_data,  # In a real system, available_sources would be different
                {"query": query, "answer": answer},
                user_persona
            )
            detailed_breakdown["sources"] = [asdict(se) for se in source_explanations]
        
        # Generate reasoning chain explanation
        if ExplanationType.REASONING_CHAIN in explanation_types:
            reasoning_explanation = self.explain_reasoning_chain(
                reasoning_data.get("steps", []),
                query, answer, user_persona, complexity
            )
            detailed_breakdown["reasoning"] = asdict(reasoning_explanation)
        
        # Generate main explanation text
        main_explanation = self._generate_main_explanation(
            query, answer, detailed_breakdown, user_persona, complexity
        )
        
        # Calculate comprehension score
        comprehension_score = self._estimate_comprehension_score(
            main_explanation, detailed_breakdown, user_persona, complexity
        )
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(
            query, answer, detailed_breakdown, user_persona
        )
        
        # Generate visualization data
        visualization_data = self._generate_visualization_data(
            detailed_breakdown, user_persona
        )
        
        return ExplanationResponse(
            explanation_id=explanation_id,
            explanation_type=ExplanationType.REASONING_CHAIN,  # Primary type
            complexity_level=complexity,
            user_persona=user_persona,
            main_explanation=main_explanation,
            detailed_breakdown=detailed_breakdown,
            confidence_level=confidence_data.get("overall_confidence", 0.0),
            comprehension_score=comprehension_score,
            follow_up_questions=follow_up_questions,
            related_explanations=[],
            visualization_data=visualization_data,
            metadata={
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "explanation_types": [et.value for et in explanation_types],
                "processing_time_ms": 0  # Would be calculated in real implementation
            }
        )
    
    def record_user_feedback(
        self,
        explanation_id: str,
        user_id: str,
        comprehension_rating: int,
        helpfulness_rating: int,
        clarity_rating: int,
        comments: str = None
    ):
        """Record user feedback on explanation quality"""
        feedback = {
            "explanation_id": explanation_id,
            "user_id": user_id,
            "comprehension_rating": comprehension_rating,  # 1-5 scale
            "helpfulness_rating": helpfulness_rating,      # 1-5 scale
            "clarity_rating": clarity_rating,              # 1-5 scale
            "comments": comments,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store feedback for improving explanations
        if explanation_id not in self.user_comprehension_data:
            self.user_comprehension_data[explanation_id] = []
        self.user_comprehension_data[explanation_id].append(feedback)
        
        # Update explanation effectiveness metrics
        self._update_explanation_effectiveness(explanation_id, feedback)
        
        self.logger.info(f"Recorded user feedback for explanation {explanation_id}")
    
    def get_explanation_analytics(
        self, explanation_id: str = None, time_period_days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics on explanation effectiveness"""
        if explanation_id:
            return self._get_single_explanation_analytics(explanation_id)
        else:
            return self._get_overall_explanation_analytics(time_period_days)
    
    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load explanation templates for different scenarios"""
        return {
            "confidence_high": "I am confident in this answer because {confidence_reasons}.",
            "confidence_medium": "I am moderately confident in this answer. {uncertainty_factors}",
            "confidence_low": "I have limited confidence in this answer due to {limitations}.",
            "source_selection": "I selected these sources because they {selection_criteria}.",
            "reasoning_simple": "To answer your question, I {reasoning_steps}.",
            "reasoning_detailed": "My reasoning process involved {detailed_steps}.",
            "uncertainty_disclosure": "Please note that {uncertainty_factors} may affect the accuracy of this answer."
        }
    
    def _identify_uncertainty_sources(self, confidence_factors: Dict[str, float]) -> List[str]:
        """Identify sources of uncertainty in the confidence assessment"""
        uncertainty_sources = []
        
        for factor, score in confidence_factors.items():
            if score < 0.6:  # Low confidence threshold
                if factor == "source_reliability":
                    uncertainty_sources.append("Limited reliability of available sources")
                elif factor == "query_clarity":
                    uncertainty_sources.append("Ambiguity in the question")
                elif factor == "domain_coverage":
                    uncertainty_sources.append("Limited coverage in this domain")
                elif factor == "consensus":
                    uncertainty_sources.append("Conflicting information from sources")
                else:
                    uncertainty_sources.append(f"Low confidence in {factor}")
        
        return uncertainty_sources
    
    def _get_confidence_calibration(
        self, confidence_score: float, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get confidence calibration information"""
        # This would typically query a database of historical predictions
        return {
            "historical_accuracy": 0.85,  # Example: 85% accuracy for similar confidence scores
            "calibration_error": 0.05,    # Example: 5% average calibration error
            "sample_size": 1000,          # Example: based on 1000 similar predictions
            "domain_accuracy": 0.82       # Example: accuracy in this specific domain
        }
    
    def _calculate_domain_confidence(
        self, confidence_factors: Dict[str, float], context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate confidence scores for different domains"""
        # This would typically use domain-specific models
        return {
            "general_knowledge": confidence_factors.get("general_knowledge", 0.8),
            "domain_specific": confidence_factors.get("domain_specific", 0.7),
            "recent_events": confidence_factors.get("recent_events", 0.6),
            "technical_accuracy": confidence_factors.get("technical_accuracy", 0.75)
        }
    
    def _generate_confidence_explanation_text(
        self,
        confidence_score: float,
        confidence_factors: Dict[str, float],
        uncertainty_sources: List[str],
        user_persona: UserPersona,
        complexity: ExplanationComplexity
    ) -> str:
        """Generate natural language explanation of confidence score"""
        if confidence_score >= 0.8:
            base_text = "I am highly confident in this answer"
        elif confidence_score >= 0.6:
            base_text = "I am moderately confident in this answer"
        else:
            base_text = "I have limited confidence in this answer"
        
        # Add details based on complexity level
        if complexity in [ExplanationComplexity.INTERMEDIATE, ExplanationComplexity.TECHNICAL]:
            factors_text = self._format_confidence_factors(confidence_factors, user_persona)
            base_text += f" based on {factors_text}"
        
        # Add uncertainty disclosure
        if uncertainty_sources and complexity != ExplanationComplexity.SIMPLE:
            uncertainty_text = ", ".join(uncertainty_sources[:2])  # Limit to prevent overwhelm
            base_text += f". Please note that {uncertainty_text.lower()} may affect accuracy"
        
        return base_text + "."
    
    def _format_confidence_factors(
        self, confidence_factors: Dict[str, float], user_persona: UserPersona
    ) -> str:
        """Format confidence factors for different user personas"""
        sorted_factors = sorted(confidence_factors.items(), key=lambda x: x[1], reverse=True)
        top_factors = sorted_factors[:3]  # Show top 3 factors
        
        factor_descriptions = {
            "source_reliability": "reliable sources",
            "query_clarity": "clear question interpretation",
            "domain_coverage": "comprehensive domain knowledge",
            "consensus": "consistent information across sources",
            "recency": "up-to-date information"
        }
        
        if user_persona == UserPersona.TECHNICAL_USER:
            # Show actual scores for technical users
            factor_text = ", ".join([
                f"{factor_descriptions.get(factor, factor)} ({score:.2f})"
                for factor, score in top_factors
            ])
        else:
            # Use descriptive language for general users
            factor_text = ", ".join([
                factor_descriptions.get(factor, factor)
                for factor, score in top_factors if score > 0.6
            ])
        
        return factor_text
    
    def _calculate_source_relevance(
        self, source: Dict[str, Any], query_context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for a source"""
        # This is a simplified implementation - would use sophisticated matching
        query = query_context.get("query", "").lower()
        source_content = source.get("content", "").lower()
        source_title = source.get("title", "").lower()
        
        # Simple keyword overlap scoring
        query_words = set(query.split())
        content_words = set(source_content.split())
        title_words = set(source_title.split())
        
        content_overlap = len(query_words.intersection(content_words)) / len(query_words) if query_words else 0
        title_overlap = len(query_words.intersection(title_words)) / len(query_words) if query_words else 0
        
        # Weight title matches higher
        relevance_score = (content_overlap * 0.7) + (title_overlap * 0.3)
        
        return min(relevance_score * 2, 1.0)  # Scale and cap at 1.0
    
    def _calculate_source_credibility(self, source: Dict[str, Any]) -> float:
        """Calculate credibility score for a source"""
        credibility_score = 0.5  # Base score
        
        # Factors that increase credibility
        if source.get("source_type") == "official_document":
            credibility_score += 0.3
        elif source.get("source_type") == "academic_paper":
            credibility_score += 0.25
        elif source.get("source_type") == "news_article":
            credibility_score += 0.1
        
        # Publication date (more recent = higher credibility for some domains)
        pub_date = source.get("publication_date")
        if pub_date:
            # Simple recency bonus (would be more sophisticated in practice)
            credibility_score += 0.1
        
        # Source reputation
        reputation = source.get("source_reputation", 0.5)
        credibility_score += reputation * 0.2
        
        return min(credibility_score, 1.0)
    
    def _generate_relevance_reasons(
        self, source: Dict[str, Any], query_context: Dict[str, Any], relevance_score: float
    ) -> List[str]:
        """Generate reasons why a source is relevant"""
        reasons = []
        
        if relevance_score > 0.8:
            reasons.append("High content alignment with your question")
        elif relevance_score > 0.6:
            reasons.append("Good content alignment with your question")
        else:
            reasons.append("Partial content alignment with your question")
        
        # Add specific reasons based on source characteristics
        if source.get("recency_score", 0) > 0.7:
            reasons.append("Contains recent information relevant to your query")
        
        if source.get("expertise_level") == "expert":
            reasons.append("Authored by domain experts")
        
        return reasons
    
    def _generate_credibility_factors(
        self, source: Dict[str, Any], credibility_score: float
    ) -> List[str]:
        """Generate factors affecting source credibility"""
        factors = []
        
        source_type = source.get("source_type", "unknown")
        if source_type == "official_document":
            factors.append("Official government or organizational document")
        elif source_type == "academic_paper":
            factors.append("Peer-reviewed academic publication")
        elif source_type == "news_article":
            factors.append("Published news article")
        
        if source.get("verification_status") == "verified":
            factors.append("Information verified through multiple sources")
        
        if credibility_score < 0.6:
            factors.append("Limited verification of claims")
        
        return factors
    
    def _identify_alternative_sources(
        self, source: Dict[str, Any], available_sources: List[Dict[str, Any]], 
        query_context: Dict[str, Any]
    ) -> List[str]:
        """Identify alternative sources that could have been used"""
        alternatives = []
        
        for alt_source in available_sources:
            if alt_source.get("id") != source.get("id"):
                relevance = self._calculate_source_relevance(alt_source, query_context)
                if relevance > 0.5:  # Threshold for considering as alternative
                    alternatives.append(alt_source.get("title", "Unnamed Source"))
        
        return alternatives[:3]  # Limit to top 3 alternatives
    
    def _identify_source_limitations(self, source: Dict[str, Any]) -> List[str]:
        """Identify limitations of a source"""
        limitations = []
        
        pub_date = source.get("publication_date")
        if pub_date and pub_date < "2020-01-01":  # Example: old information
            limitations.append("Information may be outdated")
        
        if source.get("scope") == "limited":
            limitations.append("Limited scope of coverage")
        
        if source.get("bias_score", 0.5) > 0.7:
            limitations.append("Potential bias in presentation")
        
        return limitations
    
    def _explain_source_contribution(
        self, source: Dict[str, Any], query_context: Dict[str, Any]
    ) -> str:
        """Explain how the source contributes to the answer"""
        contribution_type = source.get("contribution_type", "general_information")
        
        contributions = {
            "primary_evidence": "Provides primary evidence supporting the main answer",
            "supporting_detail": "Offers supporting details and context",
            "alternative_perspective": "Presents an alternative viewpoint",
            "background_information": "Supplies necessary background information",
            "expert_opinion": "Provides expert analysis and interpretation",
            "statistical_data": "Contributes relevant statistics and data",
            "case_study": "Offers concrete examples and case studies"
        }
        
        return contributions.get(contribution_type, "Provides relevant information for the answer")
    
    def _process_reasoning_steps(
        self, reasoning_steps: List[Dict[str, Any]], 
        complexity: ExplanationComplexity, 
        user_persona: UserPersona
    ) -> List[Dict[str, Any]]:
        """Process reasoning steps based on complexity and user persona"""
        processed_steps = []
        
        for step in reasoning_steps:
            processed_step = {
                "step_name": step.get("step_name", "Reasoning Step"),
                "description": step.get("description", ""),
                "confidence": step.get("confidence_score"),
                "duration": step.get("duration_ms")
            }
            
            # Adjust description based on complexity
            if complexity == ExplanationComplexity.SIMPLE:
                processed_step["description"] = self._simplify_description(
                    step.get("description", ""), user_persona
                )
            elif complexity == ExplanationComplexity.TECHNICAL:
                # Include technical details
                processed_step["technical_details"] = step.get("metadata", {})
                processed_step["input_data"] = step.get("input_data", {})
                processed_step["output_data"] = step.get("output_data", {})
            
            processed_steps.append(processed_step)
        
        return processed_steps
    
    def _simplify_description(self, description: str, user_persona: UserPersona) -> str:
        """Simplify technical descriptions for general users"""
        # This is a basic implementation - would use NLP techniques in practice
        simplifications = {
            "embedding": "text representation",
            "semantic similarity": "meaning similarity",
            "confidence calibration": "reliability assessment",
            "vector space": "mathematical representation",
            "retrieval augmented": "information-enhanced"
        }
        
        simplified = description
        for technical_term, simple_term in simplifications.items():
            simplified = simplified.replace(technical_term, simple_term)
        
        return simplified
    
    def _identify_logical_connections(
        self, reasoning_steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify logical connections between reasoning steps"""
        connections = []
        
        for i in range(len(reasoning_steps) - 1):
            current_step = reasoning_steps[i]
            next_step = reasoning_steps[i + 1]
            
            connection = {
                "from_step": current_step.get("step_id"),
                "to_step": next_step.get("step_id"),
                "connection_type": self._determine_connection_type(current_step, next_step),
                "strength": self._calculate_connection_strength(current_step, next_step)
            }
            
            connections.append(connection)
        
        return connections
    
    def _determine_connection_type(
        self, step1: Dict[str, Any], step2: Dict[str, Any]
    ) -> str:
        """Determine the type of logical connection between steps"""
        step1_type = step1.get("step_type", "")
        step2_type = step2.get("step_type", "")
        
        connection_patterns = {
            ("query_processing", "retrieval_search"): "sequential",
            ("retrieval_search", "document_analysis"): "causal",
            ("document_analysis", "confidence_assessment"): "evaluative",
            ("confidence_assessment", "answer_generation"): "conditional"
        }
        
        return connection_patterns.get((step1_type, step2_type), "sequential")
    
    def _calculate_connection_strength(
        self, step1: Dict[str, Any], step2: Dict[str, Any]
    ) -> float:
        """Calculate the strength of connection between steps"""
        # This would be more sophisticated in practice
        conf1 = step1.get("confidence_score", 0.5)
        conf2 = step2.get("confidence_score", 0.5)
        
        # Strong connections when both steps have high confidence
        return (conf1 + conf2) / 2
    
    def _extract_key_insights(
        self, reasoning_steps: List[Dict[str, Any]], final_answer: str
    ) -> List[str]:
        """Extract key insights from the reasoning process"""
        insights = []
        
        # Look for high-confidence steps
        high_conf_steps = [
            step for step in reasoning_steps 
            if step.get("confidence_score", 0) > 0.8
        ]
        
        for step in high_conf_steps[:3]:  # Limit to top 3
            insight = f"Key finding: {step.get('description', '').split('.')[0]}"
            insights.append(insight)
        
        return insights
    
    def _generate_alternative_reasoning_paths(
        self, reasoning_steps: List[Dict[str, Any]], query: str, 
        complexity: ExplanationComplexity
    ) -> List[Dict[str, Any]]:
        """Generate alternative reasoning approaches"""
        if complexity == ExplanationComplexity.SIMPLE:
            return []  # Don't overwhelm simple users
        
        alternatives = []
        
        # Example alternative approaches
        if any(step.get("step_type") == "retrieval_search" for step in reasoning_steps):
            alternatives.append({
                "approach": "different_search_strategy",
                "description": "Could have used broader search terms for more comprehensive results",
                "trade_offs": "Might find more sources but with potentially lower relevance"
            })
        
        return alternatives
    
    def _calculate_reasoning_quality_score(
        self, reasoning_steps: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall quality score for the reasoning process"""
        if not reasoning_steps:
            return 0.0
        
        # Factors affecting quality
        completion_rate = len([s for s in reasoning_steps if s.get("status") == "completed"]) / len(reasoning_steps)
        avg_confidence = statistics.mean([s.get("confidence_score", 0) for s in reasoning_steps])
        step_diversity = len(set(s.get("step_type") for s in reasoning_steps)) / max(len(reasoning_steps), 1)
        
        # Weighted combination
        quality_score = (completion_rate * 0.4) + (avg_confidence * 0.4) + (step_diversity * 0.2)
        
        return quality_score
    
    def _generate_reasoning_narrative(
        self, steps: List[Dict[str, Any]], key_insights: List[str], 
        user_persona: UserPersona, complexity: ExplanationComplexity
    ) -> str:
        """Generate natural language narrative of the reasoning process"""
        if complexity == ExplanationComplexity.SIMPLE:
            return self._generate_simple_narrative(steps, key_insights)
        else:
            return self._generate_detailed_narrative(steps, key_insights, user_persona)
    
    def _generate_simple_narrative(
        self, steps: List[Dict[str, Any]], key_insights: List[str]
    ) -> str:
        """Generate simple narrative for general users"""
        if not steps:
            return "I processed your question and found relevant information to provide an answer."
        
        narrative = f"To answer your question, I went through {len(steps)} main steps: "
        step_names = [step.get("step_name", "analysis") for step in steps[:3]]
        narrative += ", ".join(step_names)
        
        if key_insights:
            narrative += f". The key finding was: {key_insights[0].replace('Key finding: ', '')}"
        
        return narrative + "."
    
    def _generate_detailed_narrative(
        self, steps: List[Dict[str, Any]], key_insights: List[str], 
        user_persona: UserPersona
    ) -> str:
        """Generate detailed narrative for informed users"""
        narrative = "My reasoning process involved the following key stages:\n\n"
        
        for i, step in enumerate(steps[:5], 1):  # Limit to 5 steps for readability
            step_desc = step.get("description", "Performed analysis")
            confidence = step.get("confidence", 0)
            
            narrative += f"{i}. {step_desc}"
            if confidence and user_persona in [UserPersona.TECHNICAL_USER, UserPersona.DOMAIN_EXPERT]:
                narrative += f" (confidence: {confidence:.2f})"
            narrative += "\n"
        
        if key_insights:
            narrative += f"\nKey insights from this analysis:\n"
            for insight in key_insights[:3]:
                narrative += f"• {insight.replace('Key finding: ', '')}\n"
        
        return narrative
    
    def _generate_main_explanation(
        self, query: str, answer: str, detailed_breakdown: Dict[str, Any],
        user_persona: UserPersona, complexity: ExplanationComplexity
    ) -> str:
        """Generate the main explanation text"""
        explanation = f"To answer your question about {query.lower()}, "
        
        # Add confidence information
        confidence_info = detailed_breakdown.get("confidence", {})
        overall_confidence = confidence_info.get("overall_confidence", 0)
        
        if overall_confidence >= 0.8:
            explanation += "I found reliable information that strongly supports this answer. "
        elif overall_confidence >= 0.6:
            explanation += "I found good information that supports this answer with moderate confidence. "
        else:
            explanation += "I found some relevant information, though with limited confidence. "
        
        # Add source information
        sources_info = detailed_breakdown.get("sources", [])
        if sources_info:
            source_count = len(sources_info)
            explanation += f"This response is based on {source_count} relevant source{'s' if source_count > 1 else ''}, "
            explanation += "which I selected for their relevance and credibility. "
        
        # Add reasoning information if complex enough
        if complexity != ExplanationComplexity.SIMPLE:
            reasoning_info = detailed_breakdown.get("reasoning", {})
            if reasoning_info:
                step_count = len(reasoning_info.get("steps", []))
                explanation += f"My analysis involved {step_count} reasoning steps "
                explanation += "to ensure a thorough and accurate response."
        
        return explanation
    
    def _estimate_comprehension_score(
        self, main_explanation: str, detailed_breakdown: Dict[str, Any],
        user_persona: UserPersona, complexity: ExplanationComplexity
    ) -> float:
        """Estimate how well users will comprehend the explanation"""
        score = 0.7  # Base score
        
        # Adjust based on complexity
        complexity_adjustments = {
            ExplanationComplexity.SIMPLE: 0.2,
            ExplanationComplexity.INTERMEDIATE: 0.1,
            ExplanationComplexity.TECHNICAL: -0.1,
            ExplanationComplexity.ADAPTIVE: 0.15
        }
        score += complexity_adjustments.get(complexity, 0)
        
        # Adjust based on user persona
        persona_adjustments = {
            UserPersona.GENERAL_PUBLIC: 0.1 if complexity == ExplanationComplexity.SIMPLE else -0.1,
            UserPersona.BUSINESS_USER: 0.05,
            UserPersona.TECHNICAL_USER: 0.1 if complexity == ExplanationComplexity.TECHNICAL else 0,
            UserPersona.DOMAIN_EXPERT: 0.15,
            UserPersona.AUDITOR: 0.1,
            UserPersona.RESEARCHER: 0.1
        }
        score += persona_adjustments.get(user_persona, 0)
        
        # Adjust based on explanation length (too long = lower comprehension)
        explanation_length = len(main_explanation.split())
        if explanation_length > 150:
            score -= 0.1
        elif explanation_length < 50:
            score -= 0.05  # Too short might lack clarity
        
        return max(0.0, min(1.0, score))
    
    def _generate_follow_up_questions(
        self, query: str, answer: str, detailed_breakdown: Dict[str, Any],
        user_persona: UserPersona
    ) -> List[str]:
        """Generate relevant follow-up questions"""
        questions = []
        
        # Generic follow-ups based on confidence
        confidence_info = detailed_breakdown.get("confidence", {})
        overall_confidence = confidence_info.get("overall_confidence", 0)
        
        if overall_confidence < 0.8:
            questions.append("Would you like me to search for additional sources on this topic?")
        
        # Source-based follow-ups
        sources_info = detailed_breakdown.get("sources", [])
        if sources_info:
            questions.append("Would you like me to explain why I chose these specific sources?")
            questions.append("Are you interested in seeing alternative sources I considered?")
        
        # Reasoning-based follow-ups
        reasoning_info = detailed_breakdown.get("reasoning", {})
        if reasoning_info:
            questions.append("Would you like a more detailed explanation of my reasoning process?")
        
        # Persona-specific questions
        if user_persona == UserPersona.TECHNICAL_USER:
            questions.append("Would you like to see the technical details of my analysis?")
        elif user_persona == UserPersona.AUDITOR:
            questions.append("Would you like a compliance report for this analysis?")
        
        return questions[:3]  # Limit to 3 questions
    
    def _generate_visualization_data(
        self, detailed_breakdown: Dict[str, Any], user_persona: UserPersona
    ) -> Dict[str, Any]:
        """Generate data for visualizations"""
        viz_data = {}
        
        # Confidence visualization
        confidence_info = detailed_breakdown.get("confidence", {})
        if confidence_info:
            viz_data["confidence_chart"] = {
                "type": "gauge",
                "value": confidence_info.get("overall_confidence", 0),
                "factors": confidence_info.get("confidence_factors", {})
            }
        
        # Source visualization
        sources_info = detailed_breakdown.get("sources", [])
        if sources_info:
            viz_data["sources_chart"] = {
                "type": "bar",
                "data": [
                    {
                        "source": src.get("source_title", "Unknown"),
                        "relevance": src.get("relevance_score", 0),
                        "credibility": src.get("credibility_score", 0)
                    }
                    for src in sources_info
                ]
            }
        
        # Reasoning flow visualization
        reasoning_info = detailed_breakdown.get("reasoning", {})
        if reasoning_info and user_persona != UserPersona.GENERAL_PUBLIC:
            steps = reasoning_info.get("steps", [])
            viz_data["reasoning_flow"] = {
                "type": "flow",
                "nodes": [
                    {
                        "id": i,
                        "label": step.get("step_name", f"Step {i+1}"),
                        "confidence": step.get("confidence", 0.5)
                    }
                    for i, step in enumerate(steps)
                ],
                "connections": reasoning_info.get("logical_connections", [])
            }
        
        return viz_data
    
    def _update_explanation_effectiveness(
        self, explanation_id: str, feedback: Dict[str, Any]
    ):
        """Update effectiveness metrics based on user feedback"""
        if explanation_id not in self.explanation_effectiveness:
            self.explanation_effectiveness[explanation_id] = {
                "ratings": [],
                "average_comprehension": 0,
                "average_helpfulness": 0,
                "average_clarity": 0,
                "improvement_suggestions": []
            }
        
        effectiveness = self.explanation_effectiveness[explanation_id]
        effectiveness["ratings"].append(feedback)
        
        # Calculate averages
        ratings = effectiveness["ratings"]
        effectiveness["average_comprehension"] = statistics.mean([r["comprehension_rating"] for r in ratings])
        effectiveness["average_helpfulness"] = statistics.mean([r["helpfulness_rating"] for r in ratings])
        effectiveness["average_clarity"] = statistics.mean([r["clarity_rating"] for r in ratings])
        
        # Generate improvement suggestions based on low ratings
        if effectiveness["average_comprehension"] < 3.0:
            effectiveness["improvement_suggestions"].append("Consider simplifying explanations")
        if effectiveness["average_clarity"] < 3.0:
            effectiveness["improvement_suggestions"].append("Improve explanation structure and clarity")
    
    def _get_single_explanation_analytics(self, explanation_id: str) -> Dict[str, Any]:
        """Get analytics for a specific explanation"""
        if explanation_id not in self.explanation_effectiveness:
            return {"message": "No analytics available for this explanation"}
        
        effectiveness = self.explanation_effectiveness[explanation_id]
        feedback_data = self.user_comprehension_data.get(explanation_id, [])
        
        return {
            "explanation_id": explanation_id,
            "total_feedback": len(feedback_data),
            "average_ratings": {
                "comprehension": effectiveness["average_comprehension"],
                "helpfulness": effectiveness["average_helpfulness"],
                "clarity": effectiveness["average_clarity"]
            },
            "improvement_suggestions": effectiveness["improvement_suggestions"],
            "user_comments": [f["comments"] for f in feedback_data if f.get("comments")]
        }
    
    def _get_overall_explanation_analytics(self, time_period_days: int) -> Dict[str, Any]:
        """Get overall analytics across all explanations"""
        # This would typically query a database for time-filtered data
        total_explanations = len(self.explanation_effectiveness)
        
        if total_explanations == 0:
            return {"message": "No explanation data available"}
        
        all_comprehension = []
        all_helpfulness = []
        all_clarity = []
        
        for effectiveness in self.explanation_effectiveness.values():
            all_comprehension.append(effectiveness["average_comprehension"])
            all_helpfulness.append(effectiveness["average_helpfulness"])
            all_clarity.append(effectiveness["average_clarity"])
        
        return {
            "time_period_days": time_period_days,
            "total_explanations": total_explanations,
            "overall_averages": {
                "comprehension": statistics.mean(all_comprehension) if all_comprehension else 0,
                "helpfulness": statistics.mean(all_helpfulness) if all_helpfulness else 0,
                "clarity": statistics.mean(all_clarity) if all_clarity else 0
            },
            "comprehension_target": 0.8,  # 80% target
            "current_performance": statistics.mean(all_comprehension) if all_comprehension else 0,
            "performance_gap": 0.8 - (statistics.mean(all_comprehension) if all_comprehension else 0)
        }


# Global explainer instance
reasoning_explainer = ReasoningExplainer()


def get_reasoning_explainer() -> ReasoningExplainer:
    """Get the global reasoning explainer instance"""
    return reasoning_explainer


# Convenience functions
def explain_confidence(confidence_score: float, confidence_factors: Dict[str, float],
                      context: Dict[str, Any], user_persona: UserPersona = UserPersona.GENERAL_PUBLIC) -> ConfidenceExplanation:
    """Generate confidence explanation"""
    return reasoning_explainer.explain_confidence_score(
        confidence_score, confidence_factors, context, user_persona
    )


def explain_sources(selected_sources: List[Dict[str, Any]], available_sources: List[Dict[str, Any]],
                   query_context: Dict[str, Any], user_persona: UserPersona = UserPersona.GENERAL_PUBLIC) -> List[SourceExplanation]:
    """Generate source selection explanation"""
    return reasoning_explainer.explain_source_selection(
        selected_sources, available_sources, query_context, user_persona
    )


def explain_reasoning(reasoning_steps: List[Dict[str, Any]], query: str, final_answer: str,
                     user_persona: UserPersona = UserPersona.GENERAL_PUBLIC) -> ReasoningChainExplanation:
    """Generate reasoning chain explanation"""
    return reasoning_explainer.explain_reasoning_chain(
        reasoning_steps, query, final_answer, user_persona
    )