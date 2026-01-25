"""
Developer-grade confidence calculation system for Cognitron
Based on Thalamus DeepConf architecture with local implementation
"""

import math
import statistics
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from ..models import ConfidenceLevel, WorkflowStep, WorkflowTrace


@dataclass
class LLMCall:
    """Individual LLM call with confidence metrics"""
    call_id: str
    prompt: str
    response: str
    logprobs: List[Dict[str, float]]
    top_logprobs: List[Dict[str, float]]
    processing_time: float
    token_count: int
    timestamp: datetime


@dataclass
class ConfidenceProfile:
    """Developer-grade confidence profile for complete workflows"""
    planner_confidence: float
    steps: List[Dict[str, float]]  # [{"step_confidence": float, "tool_confidence": float}]
    overall_confidence: float
    confidence_level: ConfidenceLevel
    uncertainty_factors: List[str]
    confidence_explanation: str
    meets_developer_threshold: bool


class ConfidenceCalculator:
    """
    Developer-grade confidence calculator using DeepConf principles
    Applied to personal knowledge management with local processing
    """
    
    def __init__(self, developer_threshold: float = 0.95, production_threshold: float = 0.85):
        self.developer_threshold = developer_threshold
        self.production_threshold = production_threshold
        
    def calculate_token_confidence(self, logprobs: List[float]) -> float:
        """
        Calculate confidence for individual tokens using logprob analysis
        Based on DeepConf token-level confidence measurement
        """
        if not logprobs:
            return 0.0
            
        # Convert log probabilities to probabilities
        probs = [math.exp(logprob) for logprob in logprobs]
        
        # Use entropy-based confidence measure
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        max_entropy = math.log(len(probs))
        
        # Normalize entropy to confidence (lower entropy = higher confidence)
        if max_entropy > 0:
            confidence = 1.0 - (entropy / max_entropy)
        else:
            confidence = 1.0 if probs[0] > 0.9 else 0.0
            
        return max(0.0, min(1.0, confidence))
    
    def calculate_response_confidence(self, llm_call: LLMCall) -> float:
        """
        Calculate confidence for entire LLM response
        Uses sliding window approach from DeepConf
        """
        if not llm_call.logprobs:
            return 0.5  # Neutral confidence if no logprobs available
            
        # Extract token-level confidences
        token_confidences = []
        for token_logprobs in llm_call.logprobs:
            if isinstance(token_logprobs, dict):
                # Get confidence for the selected token
                max_logprob = max(token_logprobs.values())
                token_conf = self.calculate_token_confidence([max_logprob])
                token_confidences.append(token_conf)
        
        if not token_confidences:
            return 0.5
            
        # Use enterprise-grade confidence aggregation (minimum approach)
        # This is more conservative than average-based approaches
        return min(token_confidences)
    
    def calculate_step_confidence(self, step: WorkflowStep, llm_calls: List[LLMCall]) -> Tuple[float, float]:
        """
        Calculate confidence for individual workflow step
        Returns (step_confidence, tool_confidence)
        """
        if not llm_calls:
            return 0.5, 0.5
            
        # Calculate confidence for each LLM call in this step
        call_confidences = [self.calculate_response_confidence(call) for call in llm_calls]
        
        # Step confidence: minimum of all LLM calls (enterprise-grade conservative approach)
        step_confidence = min(call_confidences) if call_confidences else 0.5
        
        # Tool confidence: considers execution success and error rates
        tool_confidence = step_confidence
        if step.errors:
            # Penalize for errors
            error_penalty = min(0.5, len(step.errors) * 0.1)
            tool_confidence = max(0.0, tool_confidence - error_penalty)
        
        # Boost confidence for fast, error-free execution
        if step.execution_time < 1.0 and not step.errors:
            tool_confidence = min(1.0, tool_confidence + 0.1)
            
        return step_confidence, tool_confidence
    
    def calculate_planner_confidence(self, workflow_trace: WorkflowTrace) -> float:
        """
        Calculate confidence in the overall planning/routing decision
        """
        if not workflow_trace.steps:
            return 0.5
            
        # Factors affecting planner confidence
        factors = []
        
        # Step coherence: do the steps make logical sense together?
        step_count = len(workflow_trace.steps)
        if 2 <= step_count <= 5:  # Optimal step count
            factors.append(0.9)
        elif step_count == 1:  # Simple query
            factors.append(0.95)
        else:  # Too many or no steps
            factors.append(0.6)
            
        # Error rate across steps
        total_errors = sum(len(step.errors) for step in workflow_trace.steps)
        if total_errors == 0:
            factors.append(0.95)
        elif total_errors <= 2:
            factors.append(0.8)
        else:
            factors.append(0.5)
            
        # Execution time reasonableness
        avg_step_time = workflow_trace.total_execution_time / len(workflow_trace.steps)
        if avg_step_time < 2.0:  # Fast execution
            factors.append(0.9)
        elif avg_step_time < 5.0:  # Reasonable execution
            factors.append(0.8)
        else:  # Slow execution suggests complexity/problems
            factors.append(0.6)
            
        # Use minimum confidence (enterprise-grade conservative)
        return min(factors) if factors else 0.5
    
    def calculate_confidence_profile(self, workflow_trace: WorkflowTrace, llm_calls_by_step: Dict[str, List[LLMCall]]) -> ConfidenceProfile:
        """
        Calculate complete enterprise-grade confidence profile for workflow
        """
        # Calculate planner confidence
        planner_confidence = self.calculate_planner_confidence(workflow_trace)
        
        # Calculate step confidences
        step_confidences = []
        uncertainty_factors = []
        
        for step in workflow_trace.steps:
            step_llm_calls = llm_calls_by_step.get(str(step.step_id), [])
            step_conf, tool_conf = self.calculate_step_confidence(step, step_llm_calls)
            
            step_confidences.append({
                "step_confidence": step_conf,
                "tool_confidence": tool_conf
            })
            
            # Track uncertainty factors
            if step_conf < 0.8:
                uncertainty_factors.append(f"Low confidence in step: {step.step_name}")
            if step.errors:
                uncertainty_factors.append(f"Errors in step: {step.step_name}")
                
        # Calculate overall confidence using enterprise-grade approach
        all_confidences = [planner_confidence]
        for step_conf_dict in step_confidences:
            all_confidences.extend([step_conf_dict["step_confidence"], step_conf_dict["tool_confidence"]])
            
        # Use minimum confidence (most conservative developer approach)
        overall_confidence = min(all_confidences) if all_confidences else 0.0
        
        # Determine confidence level
        if overall_confidence >= self.developer_threshold:
            confidence_level = ConfidenceLevel.CRITICAL
        elif overall_confidence >= self.production_threshold:
            confidence_level = ConfidenceLevel.HIGH
        elif overall_confidence >= 0.70:
            confidence_level = ConfidenceLevel.MEDIUM
        elif overall_confidence >= 0.50:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.INSUFFICIENT
            
        # Generate confidence explanation
        confidence_explanation = self._generate_confidence_explanation(
            overall_confidence, confidence_level, uncertainty_factors
        )
        
        return ConfidenceProfile(
            planner_confidence=planner_confidence,
            steps=step_confidences,
            overall_confidence=overall_confidence,
            confidence_level=confidence_level,
            uncertainty_factors=uncertainty_factors,
            confidence_explanation=confidence_explanation,
            meets_developer_threshold=overall_confidence >= self.developer_threshold
        )
    
    def _generate_confidence_explanation(self, confidence: float, level: ConfidenceLevel, uncertainties: List[str]) -> str:
        """Generate human-readable confidence explanation"""
        
        if level == ConfidenceLevel.CRITICAL:
            explanation = f"Critical confidence ({confidence:.1%}): This response meets enterprise-grade reliability standards. Safe for important decisions."
        elif level == ConfidenceLevel.HIGH:
            explanation = f"High confidence ({confidence:.1%}): This response is production-ready but should be validated for critical decisions."
        elif level == ConfidenceLevel.MEDIUM:
            explanation = f"Medium confidence ({confidence:.1%}): This response is reasonable but requires verification for important use cases."
        elif level == ConfidenceLevel.LOW:
            explanation = f"Low confidence ({confidence:.1%}): This response has significant uncertainty and should be used cautiously."
        else:
            explanation = f"Insufficient confidence ({confidence:.1%}): This response is too unreliable for practical use."
            
        if uncertainties:
            explanation += f" Uncertainty factors: {'; '.join(uncertainties[:3])}"
            
        return explanation
    
    def should_display_result(self, confidence: float) -> bool:
        """Determine if result should be displayed based on developer standards"""
        return confidence >= 0.70  # Minimum developer threshold for display
        
    def requires_human_validation(self, confidence: float) -> bool:
        """Determine if result requires human validation"""
        return confidence < self.developer_threshold  # Below critical threshold
        
    def is_safe_for_automation(self, confidence: float) -> bool:
        """Determine if result is safe for automated decision-making"""
        return confidence >= self.production_threshold  # Production threshold


# Main function for external use
def calculate_confidence_profile(trace: WorkflowTrace, llm_calls_by_step: Optional[Dict[str, List[LLMCall]]] = None) -> ConfidenceProfile:
    """
    Calculate enterprise-grade confidence profile for a workflow trace
    
    Args:
        trace: Complete workflow execution trace
        llm_calls_by_step: Optional mapping of step IDs to LLM calls
        
    Returns:
        ConfidenceProfile with enterprise-grade confidence metrics
    """
    calculator = ConfidenceCalculator()
    if llm_calls_by_step is None:
        llm_calls_by_step = {}
    
    return calculator.calculate_confidence_profile(trace, llm_calls_by_step)


# Confidence validation utilities
def validate_confidence_calibration(predictions: List[float], actual_outcomes: List[bool]) -> Dict[str, float]:
    """
    Validate confidence calibration using developer AI standards
    
    Args:
        predictions: List of confidence scores (0.0 to 1.0)
        actual_outcomes: List of whether predictions were correct (True/False)
        
    Returns:
        Dictionary with calibration metrics
    """
    if len(predictions) != len(actual_outcomes):
        raise ValueError("Predictions and outcomes must have same length")
        
    # Bin predictions into confidence ranges
    bins = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 0.95), (0.95, 1.0)]
    calibration_metrics = {}
    
    for bin_min, bin_max in bins:
        bin_preds = []
        bin_outcomes = []
        
        for pred, outcome in zip(predictions, actual_outcomes):
            if bin_min <= pred < bin_max:
                bin_preds.append(pred)
                bin_outcomes.append(outcome)
                
        if bin_preds:
            avg_confidence = statistics.mean(bin_preds)
            accuracy = sum(bin_outcomes) / len(bin_outcomes)
            calibration_error = abs(avg_confidence - accuracy)
            
            calibration_metrics[f"{bin_min:.2f}-{bin_max:.2f}"] = {
                "average_confidence": avg_confidence,
                "accuracy": accuracy,
                "calibration_error": calibration_error,
                "sample_count": len(bin_preds)
            }
    
    # Overall calibration metrics
    overall_accuracy = sum(actual_outcomes) / len(actual_outcomes)
    overall_confidence = statistics.mean(predictions)
    overall_calibration_error = abs(overall_confidence - overall_accuracy)
    
    calibration_metrics["overall"] = {
        "accuracy": overall_accuracy,
        "average_confidence": overall_confidence,
        "calibration_error": overall_calibration_error,
        "total_samples": len(predictions)
    }
    
    return calibration_metrics