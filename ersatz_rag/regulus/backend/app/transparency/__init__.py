"""
Regulus Transparency Infrastructure
Comprehensive transparency and explainability system for the collective intelligence platform.
"""

from .reasoning_tracer import (
    ReasoningTracer,
    ReasoningStep,
    ReasoningTrace,
    ReasoningStepType,
    ReasoningStepStatus,
    get_reasoning_tracer,
    start_trace,
    add_step,
    complete_step,
    complete_trace,
    get_explanation
)

from .audit_logger import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditLevel,
    ComplianceFramework,
    get_audit_logger,
    log_user_query,
    log_document_access,
    log_answer_generation,
    generate_compliance_report
)

from .session_manager import (
    SessionManager,
    ReasoningSession,
    SessionStatus,
    SessionType,
    UserInteractionType,
    SessionMetrics,
    get_session_manager,
    create_session,
    complete_session,
    record_interaction,
    get_session_analytics
)

from .compliance_reporting import (
    ComplianceReporter,
    ComplianceReport,
    ReportType,
    ReportFormat,
    ComplianceStatus,
    ComplianceMetric,
    ComplianceViolation,
    get_compliance_reporter,
    generate_report,
    validate_compliance,
    export_report
)

__all__ = [
    # Reasoning Tracer
    "ReasoningTracer",
    "ReasoningStep", 
    "ReasoningTrace",
    "ReasoningStepType",
    "ReasoningStepStatus",
    "get_reasoning_tracer",
    "start_trace",
    "add_step",
    "complete_step",
    "complete_trace",
    "get_explanation",
    
    # Audit Logger
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditLevel",
    "ComplianceFramework",
    "get_audit_logger",
    "log_user_query",
    "log_document_access", 
    "log_answer_generation",
    "generate_compliance_report",
    
    # Session Manager
    "SessionManager",
    "ReasoningSession",
    "SessionStatus",
    "SessionType",
    "UserInteractionType",
    "SessionMetrics",
    "get_session_manager",
    "create_session",
    "complete_session",
    "record_interaction",
    "get_session_analytics",
    
    # Compliance Reporting
    "ComplianceReporter",
    "ComplianceReport",
    "ReportType",
    "ReportFormat",
    "ComplianceStatus",
    "ComplianceMetric",
    "ComplianceViolation",
    "get_compliance_reporter",
    "generate_report",
    "validate_compliance",
    "export_report"
]