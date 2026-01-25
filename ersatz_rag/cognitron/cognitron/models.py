"""
Core data models for Cognitron with enterprise-grade confidence tracking
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class ChunkType(str, Enum):
    """Types of content chunks"""
    CODE_AST = "code_ast"
    DOCUMENT_STRUCTURE = "document_structure"  
    PLAIN_TEXT = "plain_text"
    DEVELOPER_CONTENT = "developer_content"


class ConfidenceLevel(str, Enum):
    """Developer-grade confidence levels"""
    CRITICAL = "critical"      # >95% - Developer decision grade
    HIGH = "high"             # 85-95% - Production ready
    MEDIUM = "medium"         # 70-85% - Needs validation
    LOW = "low"              # 50-70% - Unreliable
    INSUFFICIENT = "insufficient"  # <50% - Do not use


class DocumentMetadata(BaseModel):
    """Metadata for indexed documents"""
    file_path: Path
    file_type: str
    file_size: int
    created_at: datetime
    modified_at: datetime
    indexed_at: datetime = Field(default_factory=datetime.now)
    chunk_count: int = 0
    processing_strategy: str = ""
    confidence_score: float = 0.0
    
    class Config:
        arbitrary_types_allowed = True


class Chunk(BaseModel):
    """A semantically coherent chunk of content with confidence tracking"""
    chunk_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chunk_type: ChunkType
    content: str
    title: Optional[str] = None
    summary: Optional[str] = None
    start_index: int = 0
    end_index: int = 0
    
    # Developer-grade confidence tracking
    extraction_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in extraction quality")
    semantic_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in semantic coherence")
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Overall chunk reliability")
    
    # Embeddings and search metadata
    embedding_vector: Optional[List[float]] = None
    topics: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    
    # Source tracking for quality assurance
    source_line_numbers: Optional[tuple] = None
    ast_node_type: Optional[str] = None  # For code chunks
    document_section: Optional[str] = None  # For document chunks
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    @model_validator(mode='before')
    @classmethod
    def calculate_overall_confidence(cls, values):
        """Calculate overall confidence from extraction and semantic confidence"""
        if isinstance(values, dict) and 'extraction_confidence' in values and 'semantic_confidence' in values:
            # Use minimum confidence (most conservative approach from developer AI)
            if 'overall_confidence' not in values:
                values['overall_confidence'] = min(values['extraction_confidence'], values['semantic_confidence'])
        return values
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get enterprise-grade confidence level"""
        if self.overall_confidence >= 0.95:
            return ConfidenceLevel.CRITICAL
        elif self.overall_confidence >= 0.85:
            return ConfidenceLevel.HIGH
        elif self.overall_confidence >= 0.70:
            return ConfidenceLevel.MEDIUM
        elif self.overall_confidence >= 0.50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.INSUFFICIENT

    class Config:
        arbitrary_types_allowed = True


class Topic(BaseModel):
    """AI-generated topic cluster with confidence metrics"""
    topic_id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    keywords: List[str]
    chunk_ids: List[UUID]
    
    # Confidence in topic quality
    clustering_confidence: float = Field(ge=0.0, le=1.0)
    labeling_confidence: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def overall_confidence(self) -> float:
        """Overall topic confidence using enterprise-grade minimum approach"""
        return min(self.clustering_confidence, self.labeling_confidence, self.coherence_score)
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get enterprise-grade confidence level for topic"""
        confidence = self.overall_confidence
        if confidence >= 0.95:
            return ConfidenceLevel.CRITICAL
        elif confidence >= 0.85:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.70:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.INSUFFICIENT


class QueryResult(BaseModel):
    """Result of a knowledge query with confidence tracking"""
    query_id: UUID = Field(default_factory=uuid4)
    query_text: str
    answer: str
    
    # Developer-grade confidence metrics
    retrieval_confidence: float = Field(ge=0.0, le=1.0)
    reasoning_confidence: float = Field(ge=0.0, le=1.0)
    factual_confidence: float = Field(ge=0.0, le=1.0)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    
    # Supporting evidence
    relevant_chunks: List[Chunk] = Field(default_factory=list)
    confidence_explanation: str = ""
    uncertainty_factors: List[str] = Field(default_factory=list)
    
    # Quality assurance
    should_display: bool = True  # Based on confidence threshold
    requires_validation: bool = False
    alternative_suggestions: List[str] = Field(default_factory=list)
    
    processing_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @model_validator(mode='before')
    @classmethod
    def calculate_overall_confidence(cls, values):
        """Calculate overall confidence using enterprise-grade minimum approach"""
        if isinstance(values, dict):
            confidences = [
                values.get('retrieval_confidence', 0.0),
                values.get('reasoning_confidence', 0.0), 
                values.get('factual_confidence', 0.0)
            ]
            if 'overall_confidence' not in values and all(c > 0 for c in confidences):
                values['overall_confidence'] = min(confidences)
        return values
    
    @model_validator(mode='before')
    @classmethod
    def determine_display_eligibility(cls, values):
        """Determine if result should be displayed based on enterprise-grade thresholds"""
        if isinstance(values, dict):
            overall_conf = values.get('overall_confidence', 0.0)
            if 'should_display' not in values:
                values['should_display'] = overall_conf >= 0.70
        return values
    
    @model_validator(mode='before')
    @classmethod
    def determine_validation_requirement(cls, values):
        """Determine if result requires human validation"""
        if isinstance(values, dict):
            overall_conf = values.get('overall_confidence', 0.0)
            if 'requires_validation' not in values:
                values['requires_validation'] = overall_conf < 0.95
        return values
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get enterprise-grade confidence level"""
        if self.overall_confidence >= 0.95:
            return ConfidenceLevel.CRITICAL
        elif self.overall_confidence >= 0.85:
            return ConfidenceLevel.HIGH
        elif self.overall_confidence >= 0.70:
            return ConfidenceLevel.MEDIUM
        elif self.overall_confidence >= 0.50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.INSUFFICIENT


class WorkflowStep(BaseModel):
    """Individual step in a multi-step workflow"""
    step_id: UUID = Field(default_factory=uuid4)
    step_name: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Step-specific confidence
    step_confidence: float = Field(ge=0.0, le=1.0)
    tool_confidence: float = Field(ge=0.0, le=1.0)
    execution_time: float = 0.0
    
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowTrace(BaseModel):
    """Complete trace of a multi-step workflow with confidence profile"""
    trace_id: UUID = Field(default_factory=uuid4)
    query: str
    outcome: str
    
    # Complete step execution trace
    steps: List[WorkflowStep] = Field(default_factory=list)
    
    # Overall workflow confidence
    planner_confidence: float = Field(ge=0.0, le=1.0)
    execution_confidence: float = Field(ge=0.0, le=1.0)
    outcome_confidence: float = Field(ge=0.0, le=1.0)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    
    # Developer-grade validation
    meets_critical_threshold: bool = False  # >95%
    safe_for_production: bool = False       # >85%
    requires_human_review: bool = True
    
    total_execution_time: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    
    @model_validator(mode='before')
    @classmethod
    def calculate_overall_confidence(cls, values):
        """Calculate overall confidence using enterprise-grade approach"""
        if isinstance(values, dict):
            # Use minimum of all confidence components (most conservative)
            confidences = [
                values.get('planner_confidence', 0.0),
                values.get('execution_confidence', 0.0),
                values.get('outcome_confidence', 0.0)
            ]
            if values.get('steps'):
                step_confidences = [step.step_confidence for step in values['steps'] if hasattr(step, 'step_confidence')]
                if step_confidences:
                    confidences.extend(step_confidences)
            
            if 'overall_confidence' not in values and confidences:
                values['overall_confidence'] = min(confidences)
        return values
    
    @model_validator(mode='before')
    @classmethod
    def check_critical_threshold(cls, values):
        """Check if workflow meets critical enterprise-grade threshold"""
        if isinstance(values, dict):
            if 'meets_critical_threshold' not in values:
                values['meets_critical_threshold'] = values.get('overall_confidence', 0.0) >= 0.95
        return values
    
    @model_validator(mode='before')
    @classmethod
    def check_production_safety(cls, values):
        """Check if workflow is safe for production use"""
        if isinstance(values, dict):
            if 'safe_for_production' not in values:
                values['safe_for_production'] = values.get('overall_confidence', 0.0) >= 0.85
        return values
    
    @model_validator(mode='before')
    @classmethod
    def check_human_review_requirement(cls, values):
        """Determine if human review is required"""
        if isinstance(values, dict):
            if 'requires_human_review' not in values:
                values['requires_human_review'] = values.get('overall_confidence', 0.0) < 0.95
        return values


class CaseMemoryEntry(BaseModel):
    """Case memory entry with confidence-based storage"""
    case_id: UUID = Field(default_factory=uuid4)
    query: str
    outcome: str
    
    # Complete workflow information
    workflow_trace: WorkflowTrace
    confidence_profile: Dict[str, Any] = Field(default_factory=dict)
    
    # Case metadata
    success: bool = True
    execution_time: float = 0.0
    retrieval_count: int = 0  # How many times this case was retrieved
    success_rate: float = 1.0  # Success rate when this case was applied
    
    # Storage eligibility (only store high-confidence cases)
    storage_confidence: float = Field(ge=0.0, le=1.0)
    eligible_for_storage: bool = False
    
    created_at: datetime = Field(default_factory=datetime.now)
    last_retrieved_at: Optional[datetime] = None
    
    @model_validator(mode='before')
    @classmethod
    def check_storage_eligibility(cls, values):
        """Only store cases that meet enterprise-grade confidence standards"""
        if isinstance(values, dict):
            storage_conf = values.get('storage_confidence', 0.0)
            workflow_trace = values.get('workflow_trace')
            
            if 'eligible_for_storage' not in values:
                if workflow_trace and hasattr(workflow_trace, 'overall_confidence'):
                    # Only store if both storage and workflow confidence are high
                    values['eligible_for_storage'] = storage_conf >= 0.85 and workflow_trace.overall_confidence >= 0.85
                else:
                    values['eligible_for_storage'] = storage_conf >= 0.85
        return values
    
    class Config:
        arbitrary_types_allowed = True