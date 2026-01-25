"""
Regulus Session Management System
Comprehensive reasoning session tracking with timestamp and duration logging
for complete transparency in the collective intelligence system.
"""

import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Status of reasoning sessions"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ABANDONED = "abandoned"


class SessionType(Enum):
    """Types of reasoning sessions"""
    QUERY_RESPONSE = "query_response"
    DOCUMENT_ANALYSIS = "document_analysis"
    BATCH_PROCESSING = "batch_processing"
    EVALUATION = "evaluation"
    TRAINING = "training"
    MAINTENANCE = "maintenance"


class UserInteractionType(Enum):
    """Types of user interactions within a session"""
    INITIAL_QUERY = "initial_query"
    FOLLOW_UP_QUESTION = "follow_up_question"
    CLARIFICATION_REQUEST = "clarification_request"
    FEEDBACK_PROVIDED = "feedback_provided"
    RESULT_RATED = "result_rated"
    SESSION_ENDED = "session_ended"


@dataclass
class SessionMetrics:
    """Comprehensive session performance metrics"""
    total_duration_ms: int
    reasoning_steps: int
    sources_accessed: int
    documents_processed: int
    api_calls_made: int
    tokens_processed: int
    confidence_scores: List[float]
    error_count: int
    user_interactions: int
    memory_usage_mb: float
    cpu_usage_percent: float


@dataclass
class UserInteraction:
    """Track user interactions within a session"""
    interaction_id: str
    interaction_type: UserInteractionType
    timestamp: datetime
    content: str
    response_time_ms: Optional[int] = None
    user_satisfaction: Optional[int] = None  # 1-5 scale
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ReasoningSession:
    """Complete reasoning session with comprehensive tracking"""
    session_id: str
    user_id: str
    session_type: SessionType
    start_time: datetime
    end_time: Optional[datetime] = None
    status: SessionStatus = SessionStatus.ACTIVE
    query: Optional[str] = None
    final_answer: Optional[str] = None
    overall_confidence: Optional[float] = None
    explanation_quality_score: Optional[float] = None
    user_satisfaction_score: Optional[int] = None
    session_metrics: Optional[SessionMetrics] = None
    user_interactions: List[UserInteraction] = None
    reasoning_trace_id: Optional[str] = None
    audit_trail_ids: List[str] = None
    context: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.user_interactions is None:
            self.user_interactions = []
        if self.audit_trail_ids is None:
            self.audit_trail_ids = []
        if self.context is None:
            self.context = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['session_type'] = self.session_type.value
        result['status'] = self.status.value
        result['start_time'] = self.start_time.isoformat()
        result['end_time'] = self.end_time.isoformat() if self.end_time else None
        
        # Convert user interactions
        result['user_interactions'] = [
            {
                **asdict(interaction),
                'interaction_type': interaction.interaction_type.value,
                'timestamp': interaction.timestamp.isoformat()
            }
            for interaction in self.user_interactions
        ]
        
        return result


class SessionManager:
    """
    Comprehensive session management system with complete transparency tracking.
    Manages reasoning sessions with timestamp and duration logging.
    """
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.active_sessions: Dict[str, ReasoningSession] = {}
        self.completed_sessions: Dict[str, ReasoningSession] = {}
        self.session_timeout_minutes = session_timeout_minutes
        self.user_sessions: Dict[str, List[str]] = defaultdict(list)  # user_id -> [session_ids]
        self.session_analytics = defaultdict(list)
        self.logger = logging.getLogger(f"{__name__}.SessionManager")
    
    def create_session(
        self,
        user_id: str,
        session_type: SessionType = SessionType.QUERY_RESPONSE,
        query: str = None,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create a new reasoning session
        
        Args:
            user_id: Unique identifier for the user
            session_type: Type of reasoning session
            query: Initial query (if applicable)
            context: Session context information
            metadata: Additional metadata
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        
        session = ReasoningSession(
            session_id=session_id,
            user_id=user_id,
            session_type=session_type,
            start_time=datetime.now(timezone.utc),
            query=query,
            context=context or {},
            metadata=metadata or {}
        )
        
        # Store session
        self.active_sessions[session_id] = session
        self.user_sessions[user_id].append(session_id)
        
        # Log initial user interaction if query provided
        if query:
            self.record_user_interaction(
                session_id, UserInteractionType.INITIAL_QUERY, query
            )
        
        self.logger.info(f"Created reasoning session {session_id} for user {user_id}")
        return session_id
    
    def update_session(
        self,
        session_id: str,
        **updates
    ) -> bool:
        """
        Update session information
        
        Args:
            session_id: Session to update
            **updates: Fields to update
            
        Returns:
            bool: Success status
        """
        session = self.active_sessions.get(session_id)
        if not session:
            self.logger.error(f"Session {session_id} not found")
            return False
        
        # Update allowed fields
        updatable_fields = [
            'query', 'final_answer', 'overall_confidence', 
            'explanation_quality_score', 'user_satisfaction_score',
            'reasoning_trace_id'
        ]
        
        for field, value in updates.items():
            if field in updatable_fields:
                setattr(session, field, value)
        
        self.logger.debug(f"Updated session {session_id}: {list(updates.keys())}")
        return True
    
    def record_user_interaction(
        self,
        session_id: str,
        interaction_type: UserInteractionType,
        content: str,
        response_time_ms: int = None,
        user_satisfaction: int = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Record a user interaction within a session
        
        Args:
            session_id: Target session
            interaction_type: Type of interaction
            content: Interaction content
            response_time_ms: System response time
            user_satisfaction: User satisfaction rating (1-5)
            metadata: Additional metadata
            
        Returns:
            interaction_id: Unique interaction identifier
        """
        session = self.active_sessions.get(session_id)
        if not session:
            self.logger.error(f"Session {session_id} not found for interaction")
            return None
        
        interaction_id = str(uuid.uuid4())
        
        interaction = UserInteraction(
            interaction_id=interaction_id,
            interaction_type=interaction_type,
            timestamp=datetime.now(timezone.utc),
            content=content,
            response_time_ms=response_time_ms,
            user_satisfaction=user_satisfaction,
            metadata=metadata or {}
        )
        
        session.user_interactions.append(interaction)
        
        self.logger.debug(f"Recorded interaction {interaction_id} for session {session_id}")
        return interaction_id
    
    def complete_session(
        self,
        session_id: str,
        final_answer: str = None,
        overall_confidence: float = None,
        explanation_quality_score: float = None,
        user_satisfaction_score: int = None,
        session_metrics: SessionMetrics = None
    ) -> bool:
        """
        Complete a reasoning session
        
        Args:
            session_id: Session to complete
            final_answer: Final answer provided
            overall_confidence: Overall confidence score
            explanation_quality_score: Quality of explanation
            user_satisfaction_score: User satisfaction (1-5)
            session_metrics: Performance metrics
            
        Returns:
            bool: Success status
        """
        session = self.active_sessions.get(session_id)
        if not session:
            self.logger.error(f"Session {session_id} not found for completion")
            return False
        
        # Update session data
        session.end_time = datetime.now(timezone.utc)
        session.status = SessionStatus.COMPLETED
        
        if final_answer is not None:
            session.final_answer = final_answer
        if overall_confidence is not None:
            session.overall_confidence = overall_confidence
        if explanation_quality_score is not None:
            session.explanation_quality_score = explanation_quality_score
        if user_satisfaction_score is not None:
            session.user_satisfaction_score = user_satisfaction_score
        if session_metrics is not None:
            session.session_metrics = session_metrics
        
        # Calculate session metrics if not provided
        if session.session_metrics is None:
            session.session_metrics = self._calculate_session_metrics(session)
        
        # Record session completion interaction
        self.record_user_interaction(
            session_id, UserInteractionType.SESSION_ENDED,
            f"Session completed with confidence {overall_confidence or 'N/A'}"
        )
        
        # Move to completed sessions
        self.completed_sessions[session_id] = session
        del self.active_sessions[session_id]
        
        # Update analytics
        self._update_session_analytics(session)
        
        self.logger.info(f"Completed reasoning session {session_id}")
        return True
    
    def fail_session(
        self,
        session_id: str,
        error_details: Dict[str, Any],
        session_metrics: SessionMetrics = None
    ) -> bool:
        """
        Mark a session as failed
        
        Args:
            session_id: Session to fail
            error_details: Details about the failure
            session_metrics: Performance metrics if available
            
        Returns:
            bool: Success status
        """
        session = self.active_sessions.get(session_id)
        if not session:
            self.logger.error(f"Session {session_id} not found for failure")
            return False
        
        session.end_time = datetime.now(timezone.utc)
        session.status = SessionStatus.FAILED
        session.metadata.update({"error_details": error_details})
        
        if session_metrics is not None:
            session.session_metrics = session_metrics
        else:
            session.session_metrics = self._calculate_session_metrics(session)
        
        # Record failure interaction
        self.record_user_interaction(
            session_id, UserInteractionType.SESSION_ENDED,
            f"Session failed: {error_details.get('error', 'Unknown error')}"
        )
        
        # Move to completed sessions (for analysis)
        self.completed_sessions[session_id] = session
        del self.active_sessions[session_id]
        
        self.logger.error(f"Failed reasoning session {session_id}: {error_details}")
        return True
    
    def get_session(self, session_id: str) -> Optional[ReasoningSession]:
        """Get session information"""
        return (self.active_sessions.get(session_id) or 
                self.completed_sessions.get(session_id))
    
    def get_user_sessions(
        self,
        user_id: str,
        status: SessionStatus = None,
        session_type: SessionType = None,
        limit: int = None
    ) -> List[ReasoningSession]:
        """
        Get sessions for a specific user
        
        Args:
            user_id: User identifier
            status: Filter by session status
            session_type: Filter by session type
            limit: Maximum number of sessions to return
            
        Returns:
            List of matching sessions
        """
        user_session_ids = self.user_sessions.get(user_id, [])
        sessions = []
        
        for session_id in user_session_ids:
            session = self.get_session(session_id)
            if not session:
                continue
            
            # Apply filters
            if status and session.status != status:
                continue
            if session_type and session.session_type != session_type:
                continue
            
            sessions.append(session)
        
        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x.start_time, reverse=True)
        
        # Apply limit
        if limit:
            sessions = sessions[:limit]
        
        return sessions
    
    def get_session_analytics(
        self,
        user_id: str = None,
        time_period_hours: int = 24,
        session_type: SessionType = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive session analytics
        
        Args:
            user_id: Filter by user (optional)
            time_period_hours: Time period for analysis
            session_type: Filter by session type (optional)
            
        Returns:
            Analytics data
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_period_hours)
        
        # Get relevant sessions
        all_sessions = list(self.completed_sessions.values())
        if user_id:
            user_session_ids = self.user_sessions.get(user_id, [])
            all_sessions = [
                self.get_session(sid) for sid in user_session_ids
                if self.get_session(sid) and sid in self.completed_sessions
            ]
        
        # Filter by time and type
        filtered_sessions = []
        for session in all_sessions:
            if not session or session.start_time < cutoff_time:
                continue
            if session_type and session.session_type != session_type:
                continue
            filtered_sessions.append(session)
        
        if not filtered_sessions:
            return {"message": "No sessions found for the specified criteria"}
        
        # Calculate analytics
        total_sessions = len(filtered_sessions)
        successful_sessions = len([s for s in filtered_sessions if s.status == SessionStatus.COMPLETED])
        failed_sessions = len([s for s in filtered_sessions if s.status == SessionStatus.FAILED])
        
        # Duration analytics
        durations = []
        confidence_scores = []
        satisfaction_scores = []
        
        for session in filtered_sessions:
            if session.end_time and session.start_time:
                duration_ms = int((session.end_time - session.start_time).total_seconds() * 1000)
                durations.append(duration_ms)
            
            if session.overall_confidence is not None:
                confidence_scores.append(session.overall_confidence)
            
            if session.user_satisfaction_score is not None:
                satisfaction_scores.append(session.user_satisfaction_score)
        
        analytics = {
            "time_period_hours": time_period_hours,
            "total_sessions": total_sessions,
            "session_status_breakdown": {
                "completed": successful_sessions,
                "failed": failed_sessions,
                "success_rate": successful_sessions / total_sessions if total_sessions > 0 else 0
            },
            "duration_analytics": {
                "average_duration_ms": statistics.mean(durations) if durations else 0,
                "median_duration_ms": statistics.median(durations) if durations else 0,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0
            },
            "quality_metrics": {
                "average_confidence": statistics.mean(confidence_scores) if confidence_scores else 0,
                "average_satisfaction": statistics.mean(satisfaction_scores) if satisfaction_scores else 0,
                "confidence_consistency": self._calculate_confidence_consistency(confidence_scores),
                "sessions_with_high_confidence": len([c for c in confidence_scores if c >= 0.8])
            },
            "user_interaction_analytics": self._calculate_interaction_analytics(filtered_sessions)
        }
        
        return analytics
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired active sessions
        
        Returns:
            Number of sessions cleaned up
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=self.session_timeout_minutes)
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.start_time < cutoff_time:
                expired_sessions.append(session_id)
        
        # Mark expired sessions as timeout
        for session_id in expired_sessions:
            session = self.active_sessions[session_id]
            session.end_time = datetime.now(timezone.utc)
            session.status = SessionStatus.TIMEOUT
            session.session_metrics = self._calculate_session_metrics(session)
            
            # Move to completed sessions
            self.completed_sessions[session_id] = session
            del self.active_sessions[session_id]
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """Get count of currently active sessions"""
        return len(self.active_sessions)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary data
        """
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        duration_ms = 0
        if session.end_time and session.start_time:
            duration_ms = int((session.end_time - session.start_time).total_seconds() * 1000)
        
        summary = {
            "session_id": session_id,
            "user_id": session.user_id,
            "session_type": session.session_type.value,
            "status": session.status.value,
            "duration_ms": duration_ms,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "query": session.query,
            "has_final_answer": bool(session.final_answer),
            "overall_confidence": session.overall_confidence,
            "explanation_quality_score": session.explanation_quality_score,
            "user_satisfaction_score": session.user_satisfaction_score,
            "user_interactions_count": len(session.user_interactions),
            "reasoning_trace_id": session.reasoning_trace_id,
            "audit_trail_count": len(session.audit_trail_ids)
        }
        
        # Add metrics summary if available
        if session.session_metrics:
            summary["performance_metrics"] = {
                "reasoning_steps": session.session_metrics.reasoning_steps,
                "sources_accessed": session.session_metrics.sources_accessed,
                "api_calls_made": session.session_metrics.api_calls_made,
                "error_count": session.session_metrics.error_count
            }
        
        return summary
    
    def export_session_data(
        self,
        session_ids: List[str] = None,
        user_id: str = None,
        export_format: str = "json"
    ) -> str:
        """
        Export session data for analysis or compliance
        
        Args:
            session_ids: Specific sessions to export (optional)
            user_id: Export all sessions for a user (optional)
            export_format: Export format ("json" or "csv")
            
        Returns:
            Exported data as string
        """
        sessions_to_export = []
        
        if session_ids:
            for session_id in session_ids:
                session = self.get_session(session_id)
                if session:
                    sessions_to_export.append(session)
        elif user_id:
            sessions_to_export = self.get_user_sessions(user_id)
        else:
            # Export all completed sessions
            sessions_to_export = list(self.completed_sessions.values())
        
        if export_format == "json":
            return json.dumps([session.to_dict() for session in sessions_to_export], indent=2)
        elif export_format == "csv":
            return self._export_sessions_to_csv(sessions_to_export)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _calculate_session_metrics(self, session: ReasoningSession) -> SessionMetrics:
        """Calculate performance metrics for a session"""
        duration_ms = 0
        if session.end_time and session.start_time:
            duration_ms = int((session.end_time - session.start_time).total_seconds() * 1000)
        
        # Extract confidence scores from user interactions and metadata
        confidence_scores = []
        if session.overall_confidence is not None:
            confidence_scores.append(session.overall_confidence)
        
        return SessionMetrics(
            total_duration_ms=duration_ms,
            reasoning_steps=session.metadata.get("reasoning_steps", 0),
            sources_accessed=session.metadata.get("sources_accessed", 0),
            documents_processed=session.metadata.get("documents_processed", 0),
            api_calls_made=session.metadata.get("api_calls_made", 0),
            tokens_processed=session.metadata.get("tokens_processed", 0),
            confidence_scores=confidence_scores,
            error_count=session.metadata.get("error_count", 0),
            user_interactions=len(session.user_interactions),
            memory_usage_mb=session.metadata.get("memory_usage_mb", 0.0),
            cpu_usage_percent=session.metadata.get("cpu_usage_percent", 0.0)
        )
    
    def _update_session_analytics(self, session: ReasoningSession):
        """Update analytics data with completed session"""
        date_key = session.start_time.date().isoformat()
        
        analytics_entry = {
            "session_id": session.session_id,
            "duration_ms": session.session_metrics.total_duration_ms if session.session_metrics else 0,
            "confidence": session.overall_confidence,
            "satisfaction": session.user_satisfaction_score,
            "status": session.status.value,
            "session_type": session.session_type.value,
            "user_interactions": len(session.user_interactions)
        }
        
        self.session_analytics[date_key].append(analytics_entry)
    
    def _calculate_confidence_consistency(self, confidence_scores: List[float]) -> float:
        """Calculate consistency of confidence scores"""
        if len(confidence_scores) < 2:
            return 1.0
        
        mean_confidence = statistics.mean(confidence_scores)
        variance = statistics.variance(confidence_scores)
        std_dev = variance ** 0.5
        
        # Normalize to 0-1 scale (lower std_dev = higher consistency)
        return max(0.0, 1.0 - (std_dev * 2))
    
    def _calculate_interaction_analytics(self, sessions: List[ReasoningSession]) -> Dict[str, Any]:
        """Calculate user interaction analytics"""
        total_interactions = 0
        interaction_types = defaultdict(int)
        response_times = []
        satisfaction_ratings = []
        
        for session in sessions:
            total_interactions += len(session.user_interactions)
            
            for interaction in session.user_interactions:
                interaction_types[interaction.interaction_type.value] += 1
                
                if interaction.response_time_ms:
                    response_times.append(interaction.response_time_ms)
                
                if interaction.user_satisfaction:
                    satisfaction_ratings.append(interaction.user_satisfaction)
        
        return {
            "total_interactions": total_interactions,
            "average_interactions_per_session": total_interactions / len(sessions) if sessions else 0,
            "interaction_type_breakdown": dict(interaction_types),
            "average_response_time_ms": statistics.mean(response_times) if response_times else 0,
            "average_interaction_satisfaction": statistics.mean(satisfaction_ratings) if satisfaction_ratings else 0
        }
    
    def _export_sessions_to_csv(self, sessions: List[ReasoningSession]) -> str:
        """Export sessions to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'session_id', 'user_id', 'session_type', 'status', 'start_time',
            'end_time', 'duration_ms', 'query', 'overall_confidence',
            'user_satisfaction_score', 'user_interactions_count'
        ])
        
        # Write data
        for session in sessions:
            duration_ms = 0
            if session.end_time and session.start_time:
                duration_ms = int((session.end_time - session.start_time).total_seconds() * 1000)
            
            writer.writerow([
                session.session_id,
                session.user_id,
                session.session_type.value,
                session.status.value,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else '',
                duration_ms,
                session.query or '',
                session.overall_confidence or '',
                session.user_satisfaction_score or '',
                len(session.user_interactions)
            ])
        
        return output.getvalue()


# Global session manager instance
session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    return session_manager


# Convenience functions
def create_session(user_id: str, session_type: SessionType = SessionType.QUERY_RESPONSE,
                  query: str = None, context: Dict[str, Any] = None) -> str:
    """Create a new reasoning session"""
    return session_manager.create_session(user_id, session_type, query, context)


def complete_session(session_id: str, final_answer: str = None, 
                    overall_confidence: float = None) -> bool:
    """Complete a reasoning session"""
    return session_manager.complete_session(session_id, final_answer, overall_confidence)


def record_interaction(session_id: str, interaction_type: UserInteractionType, 
                      content: str, response_time_ms: int = None) -> str:
    """Record a user interaction"""
    return session_manager.record_user_interaction(
        session_id, interaction_type, content, response_time_ms
    )


def get_session_analytics(user_id: str = None, time_period_hours: int = 24) -> Dict[str, Any]:
    """Get session analytics"""
    return session_manager.get_session_analytics(user_id, time_period_hours)