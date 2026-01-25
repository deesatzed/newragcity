"""
Regulus Explainable AI Module
Comprehensive AI explainability system for transparency and user comprehension.
"""

from .reasoning_explainer import (
    ReasoningExplainer,
    ExplanationType,
    ExplanationComplexity,
    UserPersona,
    SourceExplanation,
    ConfidenceExplanation,
    ReasoningChainExplanation,
    ExplanationResponse,
    get_reasoning_explainer,
    explain_confidence,
    explain_sources,
    explain_reasoning
)

__all__ = [
    "ReasoningExplainer",
    "ExplanationType",
    "ExplanationComplexity", 
    "UserPersona",
    "SourceExplanation",
    "ConfidenceExplanation",
    "ReasoningChainExplanation",
    "ExplanationResponse",
    "get_reasoning_explainer",
    "explain_confidence",
    "explain_sources",
    "explain_reasoning"
]