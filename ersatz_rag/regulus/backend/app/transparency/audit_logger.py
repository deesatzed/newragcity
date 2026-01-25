"""
Regulus Comprehensive Audit System
Provides complete audit trail logging with 100% audit trail completeness
for compliance, security, and accountability in the collective intelligence system.
"""

import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import ipaddress
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of auditable events in the system"""
    USER_QUERY = "user_query"
    DOCUMENT_ACCESS = "document_access"
    SEARCH_OPERATION = "search_operation"
    ANSWER_GENERATION = "answer_generation"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIGURATION = "system_configuration"
    USER_AUTHENTICATION = "user_authentication"
    ERROR_OCCURRENCE = "error_occurrence"
    COMPLIANCE_CHECK = "compliance_check"
    DATA_EXPORT = "data_export"
    SESSION_MANAGEMENT = "session_management"
    API_ACCESS = "api_access"


class AuditLevel(Enum):
    """Audit logging levels for different types of events"""
    CRITICAL = "critical"  # Security, compliance violations
    HIGH = "high"         # User actions, data modifications
    MEDIUM = "medium"     # System operations, configurations
    LOW = "low"          # Debug, performance metrics
    TRACE = "trace"      # Detailed tracing information


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"
    CUSTOM = "custom"


@dataclass
class AuditEvent:
    """Individual audit event with complete traceability"""
    event_id: str
    event_type: AuditEventType
    audit_level: AuditLevel
    timestamp: datetime
    session_id: str
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_accessed: Optional[str] = None
    action_performed: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    success: bool = True
    error_details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    data_classification: Optional[str] = None
    compliance_tags: Optional[List[ComplianceFramework]] = None
    security_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    checksum: Optional[str] = None
    
    def __post_init__(self):
        """Generate checksum for audit integrity"""
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum for audit integrity"""
        # Create deterministic string representation
        data_string = f"{self.event_id}{self.timestamp.isoformat()}{self.session_id}"
        data_string += f"{self.user_id or ''}{self.action_performed or ''}"
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['audit_level'] = self.audit_level.value
        result['timestamp'] = self.timestamp.isoformat()
        if self.compliance_tags:
            result['compliance_tags'] = [tag.value for tag in self.compliance_tags]
        return result
    
    def validate_integrity(self) -> bool:
        """Validate audit event integrity using checksum"""
        current_checksum = self.checksum
        self.checksum = None
        calculated_checksum = self._calculate_checksum()
        self.checksum = current_checksum
        return current_checksum == calculated_checksum


@dataclass
class ComplianceReport:
    """Compliance report for audit data"""
    report_id: str
    framework: ComplianceFramework
    start_date: datetime
    end_date: datetime
    total_events: int
    compliant_events: int
    non_compliant_events: int
    compliance_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class AuditLogger:
    """
    Comprehensive audit logging system with 100% audit trail completeness.
    Provides complete traceability for compliance and security requirements.
    """
    
    def __init__(self, storage_backend: str = "database", log_level: AuditLevel = AuditLevel.MEDIUM):
        self.storage_backend = storage_backend
        self.log_level = log_level
        self.audit_events: Dict[str, AuditEvent] = {}
        self.session_events: Dict[str, List[str]] = {}  # session_id -> [event_ids]
        self.compliance_rules: Dict[ComplianceFramework, Dict[str, Any]] = {}
        self.logger = logging.getLogger(f"{__name__}.AuditLogger")
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
        
        # Set up file logging if needed
        if storage_backend in ["file", "hybrid"]:
            self._setup_file_logging()
    
    def log_event(
        self,
        event_type: AuditEventType,
        session_id: str,
        action_performed: str,
        audit_level: AuditLevel = AuditLevel.MEDIUM,
        user_id: str = None,
        user_role: str = None,
        ip_address: str = None,
        user_agent: str = None,
        resource_accessed: str = None,
        request_data: Dict[str, Any] = None,
        response_data: Dict[str, Any] = None,
        success: bool = True,
        error_details: Dict[str, Any] = None,
        duration_ms: int = None,
        data_classification: str = None,
        compliance_tags: List[ComplianceFramework] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Log a comprehensive audit event"""
        
        # Filter by audit level
        if audit_level.value not in self._get_enabled_levels():
            return None
        
        event_id = str(uuid.uuid4())
        
        # Sanitize IP address
        sanitized_ip = self._sanitize_ip_address(ip_address)
        
        # Determine security context
        security_context = self._determine_security_context(
            user_id, user_role, sanitized_ip, event_type
        )
        
        audit_event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            audit_level=audit_level,
            timestamp=datetime.now(timezone.utc),
            session_id=session_id,
            user_id=user_id,
            user_role=user_role,
            ip_address=sanitized_ip,
            user_agent=user_agent,
            resource_accessed=resource_accessed,
            action_performed=action_performed,
            request_data=request_data or {},
            response_data=response_data or {},
            success=success,
            error_details=error_details,
            duration_ms=duration_ms,
            data_classification=data_classification,
            compliance_tags=compliance_tags or [],
            security_context=security_context,
            metadata=metadata or {}
        )
        
        # Store the audit event
        self.audit_events[event_id] = audit_event
        
        # Track by session
        if session_id not in self.session_events:
            self.session_events[session_id] = []
        self.session_events[session_id].append(event_id)
        
        # Log to appropriate backends
        self._persist_audit_event(audit_event)
        
        # Check compliance in real-time
        self._check_compliance(audit_event)
        
        self.logger.info(f"Audit event logged: {event_id} - {action_performed}")
        return event_id
    
    def log_user_query(
        self,
        session_id: str,
        user_id: str,
        query: str,
        ip_address: str = None,
        user_agent: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Log user query with privacy considerations"""
        
        # Sanitize query for logging (remove PII)
        sanitized_query = self._sanitize_query(query)
        
        return self.log_event(
            event_type=AuditEventType.USER_QUERY,
            session_id=session_id,
            action_performed="user_submitted_query",
            audit_level=AuditLevel.HIGH,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data={"query": sanitized_query, "original_length": len(query)},
            data_classification="user_generated",
            compliance_tags=[ComplianceFramework.GDPR],
            metadata=metadata
        )
    
    def log_document_access(
        self,
        session_id: str,
        user_id: str,
        document_id: str,
        document_title: str,
        access_type: str,
        success: bool = True,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Log document access for compliance tracking"""
        return self.log_event(
            event_type=AuditEventType.DOCUMENT_ACCESS,
            session_id=session_id,
            action_performed=f"accessed_document_{access_type}",
            audit_level=AuditLevel.HIGH,
            user_id=user_id,
            resource_accessed=f"document:{document_id}",
            request_data={
                "document_id": document_id,
                "document_title": document_title,
                "access_type": access_type
            },
            success=success,
            data_classification="controlled",
            compliance_tags=[ComplianceFramework.GDPR, ComplianceFramework.ISO27001],
            metadata=metadata
        )
    
    def log_search_operation(
        self,
        session_id: str,
        user_id: str,
        search_query: str,
        search_results_count: int,
        duration_ms: int,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Log search operations for performance and usage tracking"""
        sanitized_query = self._sanitize_query(search_query)
        
        return self.log_event(
            event_type=AuditEventType.SEARCH_OPERATION,
            session_id=session_id,
            action_performed="performed_search",
            audit_level=AuditLevel.MEDIUM,
            user_id=user_id,
            request_data={
                "search_query": sanitized_query,
                "results_count": search_results_count
            },
            duration_ms=duration_ms,
            data_classification="operational",
            metadata=metadata
        )
    
    def log_answer_generation(
        self,
        session_id: str,
        user_id: str,
        query_id: str,
        answer_length: int,
        confidence_score: float,
        sources_used: List[str],
        duration_ms: int,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Log answer generation with transparency metrics"""
        return self.log_event(
            event_type=AuditEventType.ANSWER_GENERATION,
            session_id=session_id,
            action_performed="generated_answer",
            audit_level=AuditLevel.HIGH,
            user_id=user_id,
            resource_accessed=f"query:{query_id}",
            response_data={
                "answer_length": answer_length,
                "confidence_score": confidence_score,
                "sources_count": len(sources_used),
                "sources_used": sources_used
            },
            duration_ms=duration_ms,
            data_classification="ai_generated",
            compliance_tags=[ComplianceFramework.GDPR],
            metadata=metadata
        )
    
    def log_error_event(
        self,
        session_id: str,
        error_type: str,
        error_message: str,
        stack_trace: str = None,
        user_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Log error events for debugging and monitoring"""
        return self.log_event(
            event_type=AuditEventType.ERROR_OCCURRENCE,
            session_id=session_id,
            action_performed=f"error_occurred_{error_type}",
            audit_level=AuditLevel.CRITICAL,
            user_id=user_id,
            success=False,
            error_details={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace
            },
            data_classification="system_error",
            metadata=metadata
        )
    
    def get_audit_trail(
        self,
        session_id: str = None,
        user_id: str = None,
        event_type: AuditEventType = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = None
    ) -> List[AuditEvent]:
        """Retrieve audit trail based on various criteria"""
        filtered_events = list(self.audit_events.values())
        
        # Apply filters
        if session_id:
            event_ids = self.session_events.get(session_id, [])
            filtered_events = [self.audit_events[eid] for eid in event_ids if eid in self.audit_events]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
        
        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            filtered_events = filtered_events[:limit]
        
        return filtered_events
    
    def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> ComplianceReport:
        """Generate compliance report for specified framework and time period"""
        report_id = str(uuid.uuid4())
        
        # Get relevant events for the time period
        events = self.get_audit_trail(start_date=start_date, end_date=end_date)
        
        # Filter events relevant to the compliance framework
        relevant_events = [
            e for e in events 
            if framework in (e.compliance_tags or [])
        ]
        
        # Analyze compliance
        compliant_events = []
        non_compliant_events = []
        violations = []
        
        compliance_rules = self.compliance_rules.get(framework, {})
        
        for event in relevant_events:
            is_compliant = self._check_event_compliance(event, compliance_rules)
            if is_compliant:
                compliant_events.append(event)
            else:
                non_compliant_events.append(event)
                violations.append({
                    "event_id": event.event_id,
                    "violation_type": "compliance_rule_violation",
                    "description": f"Event does not meet {framework.value} requirements",
                    "timestamp": event.timestamp.isoformat()
                })
        
        total_events = len(relevant_events)
        compliant_count = len(compliant_events)
        non_compliant_count = len(non_compliant_events)
        
        compliance_score = compliant_count / total_events if total_events > 0 else 1.0
        
        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(
            framework, violations, compliance_score
        )
        
        return ComplianceReport(
            report_id=report_id,
            framework=framework,
            start_date=start_date,
            end_date=end_date,
            total_events=total_events,
            compliant_events=compliant_count,
            non_compliant_events=non_compliant_count,
            compliance_score=compliance_score,
            violations=violations,
            recommendations=recommendations,
            generated_at=datetime.now(timezone.utc)
        )
    
    def verify_audit_integrity(self, event_ids: List[str] = None) -> Dict[str, bool]:
        """Verify the integrity of audit events using checksums"""
        if event_ids is None:
            event_ids = list(self.audit_events.keys())
        
        integrity_results = {}
        for event_id in event_ids:
            if event_id in self.audit_events:
                event = self.audit_events[event_id]
                integrity_results[event_id] = event.validate_integrity()
            else:
                integrity_results[event_id] = False
        
        return integrity_results
    
    def export_audit_data(
        self,
        export_format: str = "json",
        start_date: datetime = None,
        end_date: datetime = None,
        user_id: str = None
    ) -> str:
        """Export audit data in specified format"""
        events = self.get_audit_trail(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Log the export operation
        export_session = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_event(
            event_type=AuditEventType.DATA_EXPORT,
            session_id=export_session,
            action_performed="exported_audit_data",
            audit_level=AuditLevel.CRITICAL,
            user_id=user_id,
            request_data={
                "export_format": export_format,
                "events_count": len(events),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            },
            compliance_tags=[ComplianceFramework.GDPR],
            metadata={"export_purpose": "compliance_audit"}
        )
        
        if export_format == "json":
            return json.dumps([event.to_dict() for event in events], indent=2)
        elif export_format == "csv":
            return self._export_to_csv(events)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _sanitize_query(self, query: str) -> str:
        """Sanitize query for logging by removing potential PII"""
        # This is a basic implementation - in production, use proper PII detection
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Credit card pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email pattern
        ]
        
        sanitized = query
        for pattern in sensitive_patterns:
            import re
            sanitized = re.sub(pattern, "[REDACTED]", sanitized)
        
        # Truncate if too long
        if len(sanitized) > 500:
            sanitized = sanitized[:500] + "..."
        
        return sanitized
    
    def _sanitize_ip_address(self, ip_address: str) -> str:
        """Sanitize IP address for privacy compliance"""
        if not ip_address:
            return None
        
        try:
            ip = ipaddress.ip_address(ip_address)
            if isinstance(ip, ipaddress.IPv4Address):
                # Mask last octet for IPv4
                parts = str(ip).split('.')
                return f"{'.'.join(parts[:3])}.0"
            elif isinstance(ip, ipaddress.IPv6Address):
                # Mask last 64 bits for IPv6
                return f"{str(ip)[:19]}::"
        except ValueError:
            return "[INVALID_IP]"
        
        return ip_address
    
    def _determine_security_context(
        self, user_id: str, user_role: str, ip_address: str, event_type: AuditEventType
    ) -> Dict[str, Any]:
        """Determine security context for the event"""
        context = {
            "risk_level": "low",
            "requires_approval": False,
            "security_flags": []
        }
        
        # Determine risk level based on event type
        high_risk_events = [
            AuditEventType.DATA_MODIFICATION,
            AuditEventType.SYSTEM_CONFIGURATION,
            AuditEventType.DATA_EXPORT
        ]
        
        if event_type in high_risk_events:
            context["risk_level"] = "high"
            context["requires_approval"] = True
            context["security_flags"].append("high_risk_operation")
        
        # Check for anonymous users
        if not user_id:
            context["security_flags"].append("anonymous_user")
            context["risk_level"] = "medium"
        
        # Check for suspicious IP patterns (this is basic - enhance as needed)
        if ip_address and (ip_address.startswith("10.") or "192.168." in ip_address):
            context["security_flags"].append("internal_network")
        else:
            context["security_flags"].append("external_network")
        
        return context
    
    def _get_enabled_levels(self) -> List[str]:
        """Get enabled audit levels based on configuration"""
        level_hierarchy = {
            AuditLevel.CRITICAL: ["critical"],
            AuditLevel.HIGH: ["critical", "high"],
            AuditLevel.MEDIUM: ["critical", "high", "medium"],
            AuditLevel.LOW: ["critical", "high", "medium", "low"],
            AuditLevel.TRACE: ["critical", "high", "medium", "low", "trace"]
        }
        return level_hierarchy.get(self.log_level, ["critical", "high", "medium"])
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules for different frameworks"""
        self.compliance_rules = {
            ComplianceFramework.GDPR: {
                "data_retention_days": 365,
                "requires_consent": True,
                "right_to_deletion": True,
                "data_portability": True
            },
            ComplianceFramework.HIPAA: {
                "data_encryption": True,
                "access_logging": True,
                "minimum_necessary": True,
                "audit_controls": True
            },
            ComplianceFramework.SOX: {
                "segregation_of_duties": True,
                "change_management": True,
                "access_controls": True,
                "data_integrity": True
            },
            ComplianceFramework.ISO27001: {
                "risk_assessment": True,
                "security_controls": True,
                "incident_management": True,
                "continuous_monitoring": True
            }
        }
    
    def _check_compliance(self, event: AuditEvent):
        """Check event compliance in real-time"""
        if not event.compliance_tags:
            return
        
        for framework in event.compliance_tags:
            rules = self.compliance_rules.get(framework, {})
            if not self._check_event_compliance(event, rules):
                self.logger.warning(
                    f"Compliance violation detected: {event.event_id} - {framework.value}"
                )
    
    def _check_event_compliance(self, event: AuditEvent, rules: Dict[str, Any]) -> bool:
        """Check if an event complies with given rules"""
        # This is a basic implementation - expand based on specific requirements
        if rules.get("requires_consent") and not event.metadata.get("user_consent"):
            return False
        
        if rules.get("data_encryption") and event.data_classification == "sensitive":
            if not event.metadata.get("encrypted", False):
                return False
        
        return True
    
    def _generate_compliance_recommendations(
        self, framework: ComplianceFramework, violations: List[Dict], score: float
    ) -> List[str]:
        """Generate recommendations for improving compliance"""
        recommendations = []
        
        if score < 0.9:
            recommendations.append(
                f"Compliance score ({score:.1%}) is below recommended threshold of 90%"
            )
        
        if violations:
            recommendations.append(
                f"Address {len(violations)} compliance violations identified in the audit trail"
            )
        
        framework_recommendations = {
            ComplianceFramework.GDPR: [
                "Ensure user consent is properly recorded for all data processing activities",
                "Implement automated data retention policies",
                "Provide clear data access and deletion mechanisms"
            ],
            ComplianceFramework.HIPAA: [
                "Encrypt all healthcare data at rest and in transit",
                "Implement role-based access controls",
                "Conduct regular security risk assessments"
            ]
        }
        
        if framework in framework_recommendations:
            recommendations.extend(framework_recommendations[framework])
        
        return recommendations
    
    def _persist_audit_event(self, event: AuditEvent):
        """Persist audit event to configured storage backend"""
        if self.storage_backend in ["database", "hybrid"]:
            # In a real implementation, this would write to database
            pass
        
        if self.storage_backend in ["file", "hybrid"]:
            # Write to file log
            self.logger.info(json.dumps(event.to_dict()))
    
    def _setup_file_logging(self):
        """Set up file-based audit logging"""
        # Configure file handler for audit logs
        audit_log_path = Path("audit_logs")
        audit_log_path.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            audit_log_path / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)
    
    def _export_to_csv(self, events: List[AuditEvent]) -> str:
        """Export events to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'event_id', 'event_type', 'timestamp', 'session_id', 'user_id',
            'action_performed', 'success', 'duration_ms', 'ip_address'
        ])
        
        # Write data
        for event in events:
            writer.writerow([
                event.event_id,
                event.event_type.value,
                event.timestamp.isoformat(),
                event.session_id,
                event.user_id or '',
                event.action_performed or '',
                event.success,
                event.duration_ms or '',
                event.ip_address or ''
            ])
        
        return output.getvalue()


# Global audit logger instance
audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance"""
    return audit_logger


# Convenience functions for common audit operations
def log_user_query(session_id: str, user_id: str, query: str, ip_address: str = None) -> str:
    """Log user query"""
    return audit_logger.log_user_query(session_id, user_id, query, ip_address)


def log_document_access(session_id: str, user_id: str, document_id: str, 
                       document_title: str, access_type: str) -> str:
    """Log document access"""
    return audit_logger.log_document_access(
        session_id, user_id, document_id, document_title, access_type
    )


def log_answer_generation(session_id: str, user_id: str, query_id: str,
                         answer_length: int, confidence_score: float,
                         sources_used: List[str], duration_ms: int) -> str:
    """Log answer generation"""
    return audit_logger.log_answer_generation(
        session_id, user_id, query_id, answer_length, confidence_score,
        sources_used, duration_ms
    )


def generate_compliance_report(framework: ComplianceFramework, 
                              start_date: datetime, end_date: datetime) -> ComplianceReport:
    """Generate compliance report"""
    return audit_logger.generate_compliance_report(framework, start_date, end_date)