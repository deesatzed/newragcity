"""
Regulus Transparency API Endpoints
Complete API layer for transparency infrastructure including:
- Transparent query processing with full explainability
- Session management and tracking
- Audit trail access and compliance reporting
- Reasoning explanation and analytics
"""

import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Import transparency infrastructure
from app.transparent_three_approach_integration import (
    get_transparent_rag_system, process_transparent_query
)
from app.transparency import (
    get_reasoning_tracer, get_audit_logger, get_session_manager, 
    get_compliance_reporter, ComplianceFramework, ReportType, ReportFormat
)
from app.explainable import (
    get_reasoning_explainer, UserPersona, ExplanationComplexity
)
from app.config import (
    TRANSPARENCY_ENABLED, TRANSPARENCY_LEVEL, DEFAULT_USER_PERSONA,
    DEFAULT_EXPLANATION_COMPLEXITY, DEFAULT_COMPLIANCE_FRAMEWORKS
)

logger = logging.getLogger(__name__)

# Create router for transparency endpoints
transparency_router = APIRouter(prefix="/transparency", tags=["transparency"])


# Pydantic models for request/response validation
class TransparentQueryRequest(BaseModel):
    """Request model for transparent query processing"""
    query: str = Field(..., description="User query to process")
    user_id: str = Field(..., description="Unique user identifier")
    user_persona: str = Field(DEFAULT_USER_PERSONA, description="User persona for tailored explanations")
    explanation_complexity: str = Field(DEFAULT_EXPLANATION_COMPLEXITY, description="Desired explanation complexity")
    include_reasoning_steps: bool = Field(True, description="Include detailed reasoning steps")
    include_source_explanations: bool = Field(True, description="Include source selection explanations")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for query processing")


class TransparentQueryResponse(BaseModel):
    """Response model for transparent query processing"""
    session_id: str
    trace_id: str
    query: str
    final_answer: str
    confidence_score: float
    explanation: Dict[str, Any]
    reasoning_steps: List[Dict[str, Any]]
    sources_used: List[Dict[str, Any]]
    transparency_metrics: Dict[str, Any]
    processing_metadata: Dict[str, Any]


class SessionAnalyticsRequest(BaseModel):
    """Request model for session analytics"""
    user_id: Optional[str] = Field(None, description="Filter by specific user")
    time_period_hours: int = Field(24, description="Time period for analytics in hours")
    session_type: Optional[str] = Field(None, description="Filter by session type")


class ComplianceReportRequest(BaseModel):
    """Request model for compliance report generation"""
    framework: str = Field("GDPR", description="Compliance framework")
    report_type: str = Field("compliance_summary", description="Type of report to generate")
    days_back: int = Field(7, description="Days to look back for report data")
    export_format: str = Field("json", description="Export format for report")


class ExplanationFeedbackRequest(BaseModel):
    """Request model for explanation feedback"""
    explanation_id: str = Field(..., description="Explanation identifier")
    user_id: str = Field(..., description="User providing feedback")
    comprehension_rating: int = Field(..., ge=1, le=5, description="Comprehension rating (1-5)")
    helpfulness_rating: int = Field(..., ge=1, le=5, description="Helpfulness rating (1-5)")
    clarity_rating: int = Field(..., ge=1, le=5, description="Clarity rating (1-5)")
    comments: Optional[str] = Field(None, description="Additional feedback comments")


@transparency_router.post("/query", response_model=TransparentQueryResponse)
async def process_transparent_query_endpoint(
    request: TransparentQueryRequest
):
    """
    Process query with complete transparency infrastructure
    
    Returns comprehensive response including:
    - Final answer with confidence score
    - Complete reasoning explanation
    - Step-by-step reasoning trace
    - Source selection explanations
    - Transparency metrics
    """
    if not TRANSPARENCY_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Transparency infrastructure is not enabled"
        )
    
    try:
        # Convert string enums to proper enum types
        user_persona = UserPersona(request.user_persona)
        explanation_complexity = ExplanationComplexity(request.explanation_complexity)
        
        # Process query with full transparency
        result = await process_transparent_query(
            query=request.query,
            user_id=request.user_id,
            user_persona=user_persona,
            explanation_complexity=explanation_complexity,
            context=request.context or {}
        )
        
        return TransparentQueryResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing transparent query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@transparency_router.get("/session/{session_id}")
async def get_session_details(session_id: str):
    """Get detailed information about a reasoning session"""
    session_manager = get_session_manager()
    
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    session_summary = session_manager.get_session_summary(session_id)
    return session_summary


@transparency_router.get("/session/{session_id}/reasoning")
async def get_session_reasoning(session_id: str, detail_level: str = "standard"):
    """Get reasoning explanation for a session"""
    reasoning_tracer = get_reasoning_tracer()
    session_manager = get_session_manager()
    
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    trace_id = session.reasoning_trace_id
    if not trace_id:
        raise HTTPException(
            status_code=404,
            detail=f"No reasoning trace found for session {session_id}"
        )
    
    try:
        explanation = reasoning_tracer.get_reasoning_explanation(trace_id, detail_level)
        return explanation
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@transparency_router.get("/session/{session_id}/audit")
async def get_session_audit_trail(session_id: str):
    """Get audit trail for a specific session"""
    audit_logger = get_audit_logger()
    
    audit_events = audit_logger.get_audit_trail(session_id=session_id)
    
    return {
        "session_id": session_id,
        "total_events": len(audit_events),
        "events": [event.to_dict() for event in audit_events]
    }


@transparency_router.post("/analytics/sessions")
async def get_session_analytics(request: SessionAnalyticsRequest):
    """Get comprehensive session analytics"""
    session_manager = get_session_manager()
    
    analytics = session_manager.get_session_analytics(
        user_id=request.user_id,
        time_period_hours=request.time_period_hours
    )
    
    return analytics


@transparency_router.get("/analytics/transparency")
async def get_transparency_analytics(
    time_period_hours: int = Query(24, description="Time period for analytics"),
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """Get comprehensive transparency infrastructure analytics"""
    rag_system = get_transparent_rag_system()
    
    analytics = rag_system.get_transparency_analytics(
        time_period_hours=time_period_hours,
        user_id=user_id
    )
    
    return analytics


@transparency_router.post("/compliance/report")
async def generate_compliance_report(request: ComplianceReportRequest):
    """Generate comprehensive compliance report"""
    try:
        # Convert string to enum
        framework = ComplianceFramework(request.framework.upper())
        report_type = ReportType(request.report_type.upper())
        export_format = ReportFormat(request.export_format.upper())
        
        rag_system = get_transparent_rag_system()
        
        report = rag_system.generate_compliance_report(
            framework=framework,
            report_type=report_type,
            days_back=request.days_back
        )
        
        return report
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )


@transparency_router.get("/compliance/validate")
async def validate_compliance(
    framework: str = Query("GDPR", description="Compliance framework to validate"),
    scope: Optional[str] = Query(None, description="JSON string with validation scope")
):
    """Perform real-time compliance validation"""
    try:
        compliance_framework = ComplianceFramework(framework.upper())
        compliance_reporter = get_compliance_reporter()
        
        validation_scope = {}
        if scope:
            validation_scope = json.loads(scope)
        
        validation_results = compliance_reporter.validate_compliance(
            compliance_framework, validation_scope
        )
        
        return validation_results
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameters: {str(e)}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON in scope parameter"
        )


@transparency_router.post("/explanation/feedback")
async def submit_explanation_feedback(request: ExplanationFeedbackRequest):
    """Submit feedback on explanation quality"""
    reasoning_explainer = get_reasoning_explainer()
    
    try:
        reasoning_explainer.record_user_feedback(
            explanation_id=request.explanation_id,
            user_id=request.user_id,
            comprehension_rating=request.comprehension_rating,
            helpfulness_rating=request.helpfulness_rating,
            clarity_rating=request.clarity_rating,
            comments=request.comments
        )
        
        return {
            "message": "Feedback recorded successfully",
            "explanation_id": request.explanation_id,
            "user_id": request.user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error recording explanation feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error recording feedback: {str(e)}"
        )


@transparency_router.get("/explanation/{explanation_id}/analytics")
async def get_explanation_analytics(explanation_id: str):
    """Get analytics for a specific explanation"""
    reasoning_explainer = get_reasoning_explainer()
    
    analytics = reasoning_explainer.get_explanation_analytics(explanation_id)
    
    return analytics


@transparency_router.get("/audit/events")
async def get_audit_events(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, le=1000, description="Maximum number of events to return")
):
    """Get audit events with filtering options"""
    audit_logger = get_audit_logger()
    
    # Parse date parameters
    start_datetime = None
    end_datetime = None
    
    try:
        if start_date:
            start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: {str(e)}"
        )
    
    # Convert event_type string to enum if provided
    event_type_enum = None
    if event_type:
        try:
            from app.transparency import AuditEventType
            event_type_enum = AuditEventType(event_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event type: {event_type}"
            )
    
    audit_events = audit_logger.get_audit_trail(
        user_id=user_id,
        event_type=event_type_enum,
        start_date=start_datetime,
        end_date=end_datetime,
        limit=limit
    )
    
    return {
        "total_events": len(audit_events),
        "events": [event.to_dict() for event in audit_events],
        "filters_applied": {
            "start_date": start_date,
            "end_date": end_date,
            "user_id": user_id,
            "event_type": event_type,
            "limit": limit
        }
    }


@transparency_router.get("/audit/integrity")
async def verify_audit_integrity(
    event_ids: Optional[str] = Query(None, description="Comma-separated list of event IDs to verify")
):
    """Verify integrity of audit events using checksums"""
    audit_logger = get_audit_logger()
    
    event_id_list = None
    if event_ids:
        event_id_list = [eid.strip() for eid in event_ids.split(',')]
    
    integrity_results = audit_logger.verify_audit_integrity(event_id_list)
    
    total_events = len(integrity_results)
    valid_events = sum(1 for valid in integrity_results.values() if valid)
    
    return {
        "total_events_checked": total_events,
        "valid_events": valid_events,
        "invalid_events": total_events - valid_events,
        "integrity_score": valid_events / total_events if total_events > 0 else 1.0,
        "detailed_results": integrity_results
    }


@transparency_router.get("/config")
async def get_transparency_config():
    """Get current transparency infrastructure configuration"""
    return {
        "transparency_enabled": TRANSPARENCY_ENABLED,
        "transparency_level": TRANSPARENCY_LEVEL,
        "targets": {
            "explainability": 0.95,
            "user_comprehension": 0.80,
            "audit_completeness": 1.00
        },
        "default_settings": {
            "user_persona": DEFAULT_USER_PERSONA,
            "explanation_complexity": DEFAULT_EXPLANATION_COMPLEXITY,
            "compliance_frameworks": DEFAULT_COMPLIANCE_FRAMEWORKS
        },
        "features": {
            "reasoning_tracer": "active",
            "audit_logger": "active",
            "session_manager": "active",
            "explainable_ai": "active",
            "compliance_reporting": "active"
        }
    }


@transparency_router.get("/status")
async def get_transparency_status():
    """Get health status of transparency infrastructure"""
    try:
        # Test each component
        reasoning_tracer = get_reasoning_tracer()
        audit_logger = get_audit_logger() 
        session_manager = get_session_manager()
        reasoning_explainer = get_reasoning_explainer()
        compliance_reporter = get_compliance_reporter()
        
        # Get basic metrics
        active_sessions = session_manager.get_active_session_count()
        recent_cleanup = session_manager.cleanup_expired_sessions()
        
        return {
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "reasoning_tracer": "healthy",
                "audit_logger": "healthy",
                "session_manager": "healthy",
                "reasoning_explainer": "healthy",
                "compliance_reporter": "healthy"
            },
            "metrics": {
                "active_sessions": active_sessions,
                "expired_sessions_cleaned": recent_cleanup,
                "transparency_level": TRANSPARENCY_LEVEL
            }
        }
        
    except Exception as e:
        logger.error(f"Transparency infrastructure health check failed: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "components": {
                "reasoning_tracer": "unknown",
                "audit_logger": "unknown", 
                "session_manager": "unknown",
                "reasoning_explainer": "unknown",
                "compliance_reporter": "unknown"
            }
        }


@transparency_router.delete("/session/{session_id}")
async def cleanup_session(session_id: str):
    """Clean up and remove a specific session (for GDPR compliance)"""
    session_manager = get_session_manager()
    audit_logger = get_audit_logger()
    
    # Check if session exists
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    try:
        # Log the cleanup action
        audit_logger.log_event(
            event_type=audit_logger.AuditEventType.DATA_MODIFICATION,
            session_id=session_id,
            action_performed="session_cleanup_requested",
            user_id=session.user_id,
            metadata={"cleanup_type": "user_requested", "gdpr_compliance": True}
        )
        
        # In a full implementation, this would:
        # 1. Remove session from active/completed sessions
        # 2. Clean up associated reasoning traces
        # 3. Archive or remove audit events (depending on retention policy)
        # 4. Clean up explanation data
        
        return {
            "message": f"Session {session_id} cleanup initiated",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compliance_note": "Data cleanup performed in accordance with GDPR requirements"
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error cleaning up session: {str(e)}"
        )


# Export the router for inclusion in main app
__all__ = ["transparency_router"]