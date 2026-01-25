from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class PolicyDocument(Base):
    __tablename__ = "policy_documents"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String)
    effective_date = Column(DateTime)
    source_type = Column(String)
    is_archived = Column(Boolean, default=False)
    content = Column(Text)
    doc_metadata = Column(JSON)

class AuditTrail(Base):
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)
    answer = Column(Text)
    confidence_profile = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String)
    source_document_id = Column(Integer, ForeignKey('policy_documents.id'))

# Enhanced Transparency Infrastructure Models

class ReasoningSession(Base):
    """Track reasoning sessions for complete transparency"""
    __tablename__ = "reasoning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, index=True)
    end_time = Column(DateTime)
    query = Column(Text)
    final_answer = Column(Text)
    overall_confidence = Column(Float)
    explanation_quality_score = Column(Float)
    total_duration_ms = Column(Integer)
    step_count = Column(Integer)
    extra_metadata = Column(JSON)
    
    # Relationships
    reasoning_steps = relationship("ReasoningStep", back_populates="session")
    audit_events = relationship("AuditEvent", back_populates="session")

class ReasoningStep(Base):
    """Individual reasoning steps with complete traceability"""
    __tablename__ = "reasoning_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(String, unique=True, index=True)
    session_id = Column(String, ForeignKey('reasoning_sessions.session_id'), index=True)
    parent_step_id = Column(String, ForeignKey('reasoning_steps.step_id'))
    step_type = Column(String, index=True)
    step_name = Column(String)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer)
    status = Column(String, index=True)  # initiated, in_progress, completed, failed, skipped
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence_score = Column(Float)
    error_details = Column(JSON)
    extra_metadata = Column(JSON)
    
    # Relationships
    session = relationship("ReasoningSession", back_populates="reasoning_steps")
    sub_steps = relationship("ReasoningStep", remote_side=[id])

class AuditEvent(Base):
    """Comprehensive audit events for 100% audit trail completeness"""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    session_id = Column(String, ForeignKey('reasoning_sessions.session_id'), index=True)
    event_type = Column(String, index=True)
    audit_level = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String, index=True)
    user_role = Column(String)
    ip_address = Column(String)
    user_agent = Column(Text)
    resource_accessed = Column(String)
    action_performed = Column(String, index=True)
    request_data = Column(JSON)
    response_data = Column(JSON)
    success = Column(Boolean, index=True)
    error_details = Column(JSON)
    duration_ms = Column(Integer)
    data_classification = Column(String, index=True)
    compliance_tags = Column(JSON)  # Array of compliance framework tags
    security_context = Column(JSON)
    extra_metadata = Column(JSON)
    checksum = Column(String)  # SHA-256 checksum for integrity
    
    # Relationships
    session = relationship("ReasoningSession", back_populates="audit_events")

class ExplanationTemplate(Base):
    """Templates for generating explanations for different scenarios"""
    __tablename__ = "explanation_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String, unique=True, index=True)
    template_type = Column(String, index=True)  # confidence, source_selection, reasoning
    template_content = Column(Text)
    parameters = Column(JSON)
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    extra_metadata = Column(JSON)

class ComplianceReport(Base):
    """Compliance reports for audit and regulatory purposes"""
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    framework = Column(String, index=True)  # GDPR, HIPAA, SOX, etc.
    start_date = Column(DateTime, index=True)
    end_date = Column(DateTime, index=True)
    total_events = Column(Integer)
    compliant_events = Column(Integer)
    non_compliant_events = Column(Integer)
    compliance_score = Column(Float)
    violations = Column(JSON)
    recommendations = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String)
    status = Column(String, default='generated')  # generated, reviewed, approved
    extra_metadata = Column(JSON)

class ConfidenceCalibration(Base):
    """Track confidence calibration data for improving explainability"""
    __tablename__ = "confidence_calibration"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('reasoning_sessions.session_id'), index=True)
    predicted_confidence = Column(Float, index=True)
    actual_accuracy = Column(Float)
    calibration_error = Column(Float)
    model_version = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    query_type = Column(String, index=True)
    domain = Column(String, index=True)
    extra_metadata = Column(JSON)

class UserFeedback(Base):
    """User feedback on answer quality and explanations"""
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('reasoning_sessions.session_id'), index=True)
    user_id = Column(String, index=True)
    feedback_type = Column(String, index=True)  # quality, explanation, accuracy
    rating = Column(Integer)  # 1-5 scale
    comments = Column(Text)
    helpful_explanation = Column(Boolean)
    understood_reasoning = Column(Boolean)
    trust_level = Column(Integer)  # 1-5 scale
    timestamp = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(JSON)

# Create indexes for better performance
Index('idx_reasoning_sessions_user_time', ReasoningSession.user_id, ReasoningSession.start_time)
Index('idx_reasoning_steps_session_type', ReasoningStep.session_id, ReasoningStep.step_type)
Index('idx_audit_events_user_type_time', AuditEvent.user_id, AuditEvent.event_type, AuditEvent.timestamp)
Index('idx_audit_events_compliance', AuditEvent.data_classification, AuditEvent.timestamp)
Index('idx_confidence_calibration_accuracy', ConfidenceCalibration.predicted_confidence, ConfidenceCalibration.actual_accuracy)
Index('idx_user_feedback_session_type', UserFeedback.session_id, UserFeedback.feedback_type)
