"""
Regulus Reasoning Tracer System
Provides comprehensive step-by-step reasoning logging and explanation generation
for complete transparency in the collective intelligence system.
"""

import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

logger = logging.getLogger(__name__)


class ReasoningStepType(Enum):
    """Types of reasoning steps for categorization"""
    QUERY_PROCESSING = "query_processing"
    RETRIEVAL_SEARCH = "retrieval_search"
    DOCUMENT_ANALYSIS = "document_analysis"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    ANSWER_GENERATION = "answer_generation"
    VALIDATION = "validation"
    FINAL_SYNTHESIS = "final_synthesis"
    ERROR_HANDLING = "error_handling"
    USER_INTERACTION = "user_interaction"


class ReasoningStepStatus(Enum):
    """Status tracking for reasoning steps"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ReasoningStep:
    """Individual reasoning step with complete traceability"""
    step_id: str
    step_type: ReasoningStepType
    step_name: str
    description: str
    timestamp: datetime
    duration_ms: Optional[int] = None
    status: ReasoningStepStatus = ReasoningStepStatus.INITIATED
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    error_details: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    sub_steps: Optional[List['ReasoningStep']] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['step_type'] = self.step_type.value
        result['status'] = self.status.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class ReasoningTrace:
    """Complete reasoning trace for a query session"""
    trace_id: str
    session_id: str
    query: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[int] = None
    steps: List[ReasoningStep] = None
    final_answer: Optional[str] = None
    overall_confidence: Optional[float] = None
    explanation_quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['start_time'] = self.start_time.isoformat()
        result['end_time'] = self.end_time.isoformat() if self.end_time else None
        result['steps'] = [step.to_dict() for step in self.steps]
        return result


class ReasoningTracer:
    """
    Main reasoning tracer for comprehensive step-by-step reasoning logging.
    Target: 95% reasoning step explainability
    """
    
    def __init__(self):
        self.active_traces: Dict[str, ReasoningTrace] = {}
        self.completed_traces: Dict[str, ReasoningTrace] = {}
        self.step_stack: List[ReasoningStep] = []
        self.logger = logging.getLogger(f"{__name__}.ReasoningTracer")
        
    def start_reasoning_trace(self, query: str, session_id: str, metadata: Dict[str, Any] = None) -> str:
        """Start a new reasoning trace for a query"""
        trace_id = str(uuid.uuid4())
        
        trace = ReasoningTrace(
            trace_id=trace_id,
            session_id=session_id,
            query=query,
            start_time=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        
        self.active_traces[trace_id] = trace
        
        self.logger.info(f"Started reasoning trace {trace_id} for session {session_id}")
        return trace_id
    
    def add_reasoning_step(
        self,
        trace_id: str,
        step_type: ReasoningStepType,
        step_name: str,
        description: str,
        input_data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a new reasoning step to the trace"""
        if trace_id not in self.active_traces:
            raise ValueError(f"No active trace found for trace_id: {trace_id}")
        
        step_id = str(uuid.uuid4())
        step = ReasoningStep(
            step_id=step_id,
            step_type=step_type,
            step_name=step_name,
            description=description,
            timestamp=datetime.now(timezone.utc),
            input_data=input_data or {},
            metadata=metadata or {},
            status=ReasoningStepStatus.INITIATED
        )
        
        self.active_traces[trace_id].steps.append(step)
        self.step_stack.append(step)
        
        self.logger.debug(f"Added reasoning step {step_id}: {step_name}")
        return step_id
    
    def update_step_progress(
        self,
        trace_id: str,
        step_id: str,
        status: ReasoningStepStatus,
        output_data: Dict[str, Any] = None,
        confidence_score: float = None,
        error_details: Dict[str, Any] = None
    ):
        """Update the progress of a reasoning step"""
        if trace_id not in self.active_traces:
            raise ValueError(f"No active trace found for trace_id: {trace_id}")
        
        trace = self.active_traces[trace_id]
        step = None
        
        # Find the step to update
        for s in trace.steps:
            if s.step_id == step_id:
                step = s
                break
        
        if not step:
            raise ValueError(f"No step found with step_id: {step_id}")
        
        step.status = status
        if output_data:
            step.output_data = output_data
        if confidence_score is not None:
            step.confidence_score = confidence_score
        if error_details:
            step.error_details = error_details
        
        # Calculate duration if completed or failed
        if status in [ReasoningStepStatus.COMPLETED, ReasoningStepStatus.FAILED]:
            duration = (datetime.now(timezone.utc) - step.timestamp).total_seconds() * 1000
            step.duration_ms = int(duration)
            
            # Remove from stack if it's the current step
            if self.step_stack and self.step_stack[-1].step_id == step_id:
                self.step_stack.pop()
        
        self.logger.debug(f"Updated step {step_id} status to {status.value}")
    
    def add_sub_step(
        self,
        trace_id: str,
        parent_step_id: str,
        step_type: ReasoningStepType,
        step_name: str,
        description: str,
        input_data: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Add a sub-step to an existing reasoning step"""
        if trace_id not in self.active_traces:
            raise ValueError(f"No active trace found for trace_id: {trace_id}")
        
        trace = self.active_traces[trace_id]
        parent_step = None
        
        # Find the parent step
        for step in trace.steps:
            if step.step_id == parent_step_id:
                parent_step = step
                break
        
        if not parent_step:
            raise ValueError(f"No parent step found with step_id: {parent_step_id}")
        
        step_id = str(uuid.uuid4())
        sub_step = ReasoningStep(
            step_id=step_id,
            step_type=step_type,
            step_name=step_name,
            description=description,
            timestamp=datetime.now(timezone.utc),
            input_data=input_data or {},
            metadata=metadata or {}
        )
        
        if parent_step.sub_steps is None:
            parent_step.sub_steps = []
        parent_step.sub_steps.append(sub_step)
        
        self.logger.debug(f"Added sub-step {step_id} to parent {parent_step_id}: {step_name}")
        return step_id
    
    def complete_reasoning_trace(
        self,
        trace_id: str,
        final_answer: str,
        overall_confidence: float,
        explanation_quality_score: float = None
    ):
        """Complete a reasoning trace with final results"""
        if trace_id not in self.active_traces:
            raise ValueError(f"No active trace found for trace_id: {trace_id}")
        
        trace = self.active_traces[trace_id]
        trace.end_time = datetime.now(timezone.utc)
        trace.total_duration_ms = int((trace.end_time - trace.start_time).total_seconds() * 1000)
        trace.final_answer = final_answer
        trace.overall_confidence = overall_confidence
        trace.explanation_quality_score = explanation_quality_score or self._calculate_explanation_quality(trace)
        
        # Move from active to completed traces
        self.completed_traces[trace_id] = trace
        del self.active_traces[trace_id]
        
        self.logger.info(f"Completed reasoning trace {trace_id} with confidence {overall_confidence:.3f}")
    
    def fail_reasoning_trace(self, trace_id: str, error_details: Dict[str, Any]):
        """Mark a reasoning trace as failed"""
        if trace_id not in self.active_traces:
            raise ValueError(f"No active trace found for trace_id: {trace_id}")
        
        trace = self.active_traces[trace_id]
        trace.end_time = datetime.now(timezone.utc)
        trace.total_duration_ms = int((trace.end_time - trace.start_time).total_seconds() * 1000)
        
        # Add failure step
        self.add_reasoning_step(
            trace_id,
            ReasoningStepType.ERROR_HANDLING,
            "Reasoning Failure",
            f"Reasoning trace failed: {error_details.get('error', 'Unknown error')}",
            metadata=error_details
        )
        
        # Move to completed traces
        self.completed_traces[trace_id] = trace
        del self.active_traces[trace_id]
        
        self.logger.error(f"Failed reasoning trace {trace_id}: {error_details}")
    
    def get_reasoning_explanation(self, trace_id: str, detail_level: str = "standard") -> Dict[str, Any]:
        """
        Generate human-readable explanation of reasoning process
        
        Args:
            trace_id: The trace to explain
            detail_level: 'summary', 'standard', or 'detailed'
            
        Returns:
            Structured explanation of the reasoning process
        """
        trace = self.completed_traces.get(trace_id) or self.active_traces.get(trace_id)
        if not trace:
            raise ValueError(f"No trace found for trace_id: {trace_id}")
        
        explanation = {
            "trace_id": trace_id,
            "query": trace.query,
            "reasoning_summary": self._generate_reasoning_summary(trace),
            "confidence_analysis": self._generate_confidence_analysis(trace),
            "key_steps": self._extract_key_steps(trace, detail_level),
            "explanation_quality": trace.explanation_quality_score,
            "total_duration_ms": trace.total_duration_ms,
            "step_count": len(trace.steps)
        }
        
        if detail_level == "detailed":
            explanation["full_step_trace"] = [step.to_dict() for step in trace.steps]
        
        return explanation
    
    def get_trace_statistics(self, trace_id: str) -> Dict[str, Any]:
        """Get statistical analysis of a reasoning trace"""
        trace = self.completed_traces.get(trace_id) or self.active_traces.get(trace_id)
        if not trace:
            raise ValueError(f"No trace found for trace_id: {trace_id}")
        
        step_types = {}
        confidence_scores = []
        durations = []
        
        for step in trace.steps:
            step_type = step.step_type.value
            step_types[step_type] = step_types.get(step_type, 0) + 1
            
            if step.confidence_score is not None:
                confidence_scores.append(step.confidence_score)
            if step.duration_ms is not None:
                durations.append(step.duration_ms)
        
        stats = {
            "trace_id": trace_id,
            "total_steps": len(trace.steps),
            "step_type_distribution": step_types,
            "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else None,
            "average_step_duration_ms": sum(durations) / len(durations) if durations else None,
            "total_duration_ms": trace.total_duration_ms,
            "explanation_quality": trace.explanation_quality_score
        }
        
        return stats
    
    def _calculate_explanation_quality(self, trace: ReasoningTrace) -> float:
        """Calculate explanation quality score based on trace completeness"""
        quality_factors = []
        
        # Step completeness
        completed_steps = sum(1 for step in trace.steps if step.status == ReasoningStepStatus.COMPLETED)
        total_steps = len(trace.steps)
        if total_steps > 0:
            quality_factors.append(completed_steps / total_steps)
        
        # Confidence coverage
        steps_with_confidence = sum(1 for step in trace.steps if step.confidence_score is not None)
        if total_steps > 0:
            quality_factors.append(steps_with_confidence / total_steps)
        
        # Description completeness
        well_described_steps = sum(1 for step in trace.steps if len(step.description) > 20)
        if total_steps > 0:
            quality_factors.append(well_described_steps / total_steps)
        
        # Step type diversity (more types indicate thorough reasoning)
        unique_step_types = len(set(step.step_type for step in trace.steps))
        max_types = len(ReasoningStepType)
        quality_factors.append(min(unique_step_types / max_types, 1.0))
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
    
    def _generate_reasoning_summary(self, trace: ReasoningTrace) -> str:
        """Generate a natural language summary of the reasoning process"""
        step_types = [step.step_type.value for step in trace.steps]
        unique_types = list(set(step_types))
        
        summary = f"To answer the query '{trace.query}', I followed a {len(trace.steps)}-step reasoning process. "
        
        if "query_processing" in unique_types:
            summary += "First, I analyzed and understood the question. "
        if "retrieval_search" in unique_types:
            summary += "Then I searched through relevant documents. "
        if "document_analysis" in unique_types:
            summary += "I carefully analyzed the retrieved information. "
        if "confidence_assessment" in unique_types:
            summary += "I assessed the reliability of the information. "
        if "answer_generation" in unique_types:
            summary += "Finally, I synthesized the findings into a comprehensive answer. "
        
        if trace.overall_confidence:
            confidence_desc = "high" if trace.overall_confidence > 0.8 else "moderate" if trace.overall_confidence > 0.6 else "low"
            summary += f"The overall confidence in this answer is {confidence_desc} ({trace.overall_confidence:.1%})."
        
        return summary
    
    def _generate_confidence_analysis(self, trace: ReasoningTrace) -> Dict[str, Any]:
        """Generate detailed confidence analysis"""
        confidence_scores = [step.confidence_score for step in trace.steps if step.confidence_score is not None]
        
        if not confidence_scores:
            return {"message": "No confidence scores available"}
        
        return {
            "overall_confidence": trace.overall_confidence,
            "step_confidence_range": {
                "min": min(confidence_scores),
                "max": max(confidence_scores),
                "average": sum(confidence_scores) / len(confidence_scores)
            },
            "confidence_consistency": self._calculate_confidence_consistency(confidence_scores),
            "low_confidence_steps": [
                step.step_name for step in trace.steps 
                if step.confidence_score and step.confidence_score < 0.6
            ]
        }
    
    def _extract_key_steps(self, trace: ReasoningTrace, detail_level: str) -> List[Dict[str, Any]]:
        """Extract key reasoning steps based on detail level"""
        if detail_level == "summary":
            # Return only the most important steps
            key_types = [ReasoningStepType.QUERY_PROCESSING, ReasoningStepType.RETRIEVAL_SEARCH, 
                        ReasoningStepType.FINAL_SYNTHESIS]
            key_steps = [step for step in trace.steps if step.step_type in key_types]
        else:
            # Return all steps for standard and detailed levels
            key_steps = trace.steps
        
        return [
            {
                "step_name": step.step_name,
                "description": step.description,
                "confidence": step.confidence_score,
                "duration_ms": step.duration_ms,
                "status": step.status.value
            }
            for step in key_steps
        ]
    
    def _calculate_confidence_consistency(self, confidence_scores: List[float]) -> float:
        """Calculate how consistent confidence scores are across steps"""
        if len(confidence_scores) < 2:
            return 1.0
        
        mean_confidence = sum(confidence_scores) / len(confidence_scores)
        variance = sum((score - mean_confidence) ** 2 for score in confidence_scores) / len(confidence_scores)
        std_dev = variance ** 0.5
        
        # Normalize to 0-1 scale (lower std_dev = higher consistency)
        return max(0.0, 1.0 - (std_dev * 2))


# Global tracer instance
reasoning_tracer = ReasoningTracer()


def get_reasoning_tracer() -> ReasoningTracer:
    """Get the global reasoning tracer instance"""
    return reasoning_tracer


# Convenience functions for common operations
def start_trace(query: str, session_id: str, metadata: Dict[str, Any] = None) -> str:
    """Start a new reasoning trace"""
    return reasoning_tracer.start_reasoning_trace(query, session_id, metadata)


def add_step(trace_id: str, step_type: ReasoningStepType, step_name: str, 
            description: str, input_data: Dict[str, Any] = None) -> str:
    """Add a reasoning step"""
    return reasoning_tracer.add_reasoning_step(trace_id, step_type, step_name, description, input_data)


def complete_step(trace_id: str, step_id: str, output_data: Dict[str, Any] = None, 
                 confidence_score: float = None):
    """Complete a reasoning step"""
    reasoning_tracer.update_step_progress(
        trace_id, step_id, ReasoningStepStatus.COMPLETED, output_data, confidence_score
    )


def complete_trace(trace_id: str, final_answer: str, overall_confidence: float):
    """Complete a reasoning trace"""
    reasoning_tracer.complete_reasoning_trace(trace_id, final_answer, overall_confidence)


def get_explanation(trace_id: str, detail_level: str = "standard") -> Dict[str, Any]:
    """Get explanation for a reasoning trace"""
    return reasoning_tracer.get_reasoning_explanation(trace_id, detail_level)