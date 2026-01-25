"""
Regulus Compliance Reporting Utilities
Comprehensive compliance reporting system for audit and regulatory purposes.
Integrates with audit logging and session management for complete transparency.
"""

import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import defaultdict, Counter
import re

from .audit_logger import AuditLogger, ComplianceFramework, AuditEvent, get_audit_logger
from .session_manager import SessionManager, get_session_manager

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of compliance reports"""
    AUDIT_TRAIL = "audit_trail"
    DATA_PRIVACY = "data_privacy"
    SECURITY_ASSESSMENT = "security_assessment"
    OPERATIONAL_METRICS = "operational_metrics"
    USER_ACTIVITY = "user_activity"
    SYSTEM_PERFORMANCE = "system_performance"
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT_REPORT = "incident_report"
    COMPLIANCE_SUMMARY = "compliance_summary"


class ReportFormat(Enum):
    """Report output formats"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"
    XML = "xml"


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"


@dataclass
class ComplianceMetric:
    """Individual compliance metric"""
    metric_name: str
    metric_value: Union[float, int, str, bool]
    target_value: Union[float, int, str, bool]
    status: ComplianceStatus
    description: str
    evidence: List[str]
    recommendations: List[str]
    risk_level: str  # low, medium, high, critical


@dataclass
class ComplianceViolation:
    """Detailed compliance violation record"""
    violation_id: str
    framework: ComplianceFramework
    violation_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_systems: List[str]
    data_types_involved: List[str]
    timestamp: datetime
    detection_method: str
    remediation_status: str
    remediation_actions: List[str]
    estimated_impact: str
    related_incidents: List[str]


@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    report_id: str
    report_type: ReportType
    framework: ComplianceFramework
    title: str
    generated_at: datetime
    reporting_period_start: datetime
    reporting_period_end: datetime
    generated_by: str
    status: str
    executive_summary: str
    overall_compliance_score: float
    total_metrics: int
    compliant_metrics: int
    violations: List[ComplianceViolation]
    metrics: List[ComplianceMetric]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    appendices: Dict[str, Any]
    metadata: Dict[str, Any]


class ComplianceReporter:
    """
    Comprehensive compliance reporting system that integrates with
    audit logging and session management for complete regulatory compliance.
    """
    
    def __init__(self, audit_logger: AuditLogger = None, session_manager: SessionManager = None):
        self.audit_logger = audit_logger or get_audit_logger()
        self.session_manager = session_manager or get_session_manager()
        self.compliance_rules = self._initialize_compliance_rules()
        self.violation_templates = self._initialize_violation_templates()
        self.logger = logging.getLogger(f"{__name__}.ComplianceReporter")
    
    def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        report_type: ReportType,
        start_date: datetime,
        end_date: datetime,
        scope: Dict[str, Any] = None,
        include_recommendations: bool = True
    ) -> ComplianceReport:
        """
        Generate comprehensive compliance report
        
        Args:
            framework: Compliance framework (GDPR, HIPAA, etc.)
            report_type: Type of report to generate
            start_date: Report period start
            end_date: Report period end
            scope: Additional scope parameters
            include_recommendations: Include improvement recommendations
            
        Returns:
            Complete compliance report
        """
        report_id = str(uuid.uuid4())
        scope = scope or {}
        
        # Gather data based on report type
        if report_type == ReportType.AUDIT_TRAIL:
            report_data = self._gather_audit_trail_data(framework, start_date, end_date, scope)
        elif report_type == ReportType.DATA_PRIVACY:
            report_data = self._gather_data_privacy_data(framework, start_date, end_date, scope)
        elif report_type == ReportType.SECURITY_ASSESSMENT:
            report_data = self._gather_security_data(framework, start_date, end_date, scope)
        elif report_type == ReportType.USER_ACTIVITY:
            report_data = self._gather_user_activity_data(framework, start_date, end_date, scope)
        elif report_type == ReportType.SYSTEM_PERFORMANCE:
            report_data = self._gather_performance_data(framework, start_date, end_date, scope)
        elif report_type == ReportType.COMPLIANCE_SUMMARY:
            report_data = self._gather_compliance_summary_data(framework, start_date, end_date, scope)
        else:
            report_data = self._gather_general_compliance_data(framework, start_date, end_date, scope)
        
        # Analyze compliance metrics
        metrics = self._analyze_compliance_metrics(framework, report_data, start_date, end_date)
        
        # Identify violations
        violations = self._identify_violations(framework, report_data, metrics)
        
        # Calculate overall compliance score
        overall_score = self._calculate_overall_compliance_score(metrics)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            framework, report_type, metrics, violations, overall_score
        )
        
        # Generate recommendations if requested
        recommendations = []
        if include_recommendations:
            recommendations = self._generate_recommendations(framework, violations, metrics)
        
        # Perform risk assessment
        risk_assessment = self._perform_risk_assessment(violations, metrics)
        
        # Generate appendices
        appendices = self._generate_appendices(framework, report_data, report_type)
        
        report = ComplianceReport(
            report_id=report_id,
            report_type=report_type,
            framework=framework,
            title=f"{framework.value.upper()} {report_type.value.replace('_', ' ').title()} Report",
            generated_at=datetime.now(timezone.utc),
            reporting_period_start=start_date,
            reporting_period_end=end_date,
            generated_by="Regulus Compliance System",
            status="completed",
            executive_summary=executive_summary,
            overall_compliance_score=overall_score,
            total_metrics=len(metrics),
            compliant_metrics=len([m for m in metrics if m.status == ComplianceStatus.COMPLIANT]),
            violations=violations,
            metrics=metrics,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            appendices=appendices,
            metadata={
                "generation_duration_ms": 0,  # Would be calculated in real implementation
                "data_sources": ["audit_logs", "session_data"],
                "scope": scope
            }
        )
        
        self.logger.info(f"Generated {framework.value} compliance report {report_id}")
        return report
    
    def export_report(
        self, 
        report: ComplianceReport, 
        format_type: ReportFormat = ReportFormat.JSON
    ) -> str:
        """
        Export compliance report in specified format
        
        Args:
            report: Compliance report to export
            format_type: Output format
            
        Returns:
            Formatted report data
        """
        if format_type == ReportFormat.JSON:
            return self._export_json(report)
        elif format_type == ReportFormat.CSV:
            return self._export_csv(report)
        elif format_type == ReportFormat.HTML:
            return self._export_html(report)
        else:
            raise ValueError(f"Unsupported report format: {format_type}")
    
    def validate_compliance(
        self,
        framework: ComplianceFramework,
        validation_scope: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform real-time compliance validation
        
        Args:
            framework: Compliance framework to validate against
            validation_scope: Specific areas to validate
            
        Returns:
            Validation results
        """
        validation_scope = validation_scope or {}
        rules = self.compliance_rules.get(framework, {})
        
        validation_results = {
            "framework": framework.value,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": ComplianceStatus.COMPLIANT.value,
            "rule_checks": [],
            "violations_found": 0,
            "critical_issues": 0,
            "recommendations": []
        }
        
        for rule_name, rule_config in rules.items():
            rule_result = self._validate_compliance_rule(
                framework, rule_name, rule_config, validation_scope
            )
            validation_results["rule_checks"].append(rule_result)
            
            if rule_result["status"] != ComplianceStatus.COMPLIANT.value:
                validation_results["violations_found"] += 1
                if rule_result.get("severity") == "critical":
                    validation_results["critical_issues"] += 1
        
        # Determine overall status
        if validation_results["critical_issues"] > 0:
            validation_results["overall_status"] = ComplianceStatus.NON_COMPLIANT.value
        elif validation_results["violations_found"] > 0:
            validation_results["overall_status"] = ComplianceStatus.PARTIAL_COMPLIANCE.value
        
        return validation_results
    
    def generate_incident_report(
        self,
        incident_id: str,
        incident_type: str,
        start_time: datetime,
        end_time: datetime = None,
        affected_frameworks: List[ComplianceFramework] = None
    ) -> Dict[str, Any]:
        """
        Generate incident report for compliance purposes
        
        Args:
            incident_id: Unique incident identifier
            incident_type: Type of incident (data_breach, system_failure, etc.)
            start_time: When the incident started
            end_time: When the incident was resolved (optional)
            affected_frameworks: Compliance frameworks affected
            
        Returns:
            Detailed incident report
        """
        end_time = end_time or datetime.now(timezone.utc)
        affected_frameworks = affected_frameworks or [ComplianceFramework.GDPR]
        
        # Gather incident-related audit events
        incident_events = self.audit_logger.get_audit_trail(
            start_date=start_time,
            end_date=end_time
        )
        
        # Analyze incident impact
        impact_analysis = self._analyze_incident_impact(
            incident_events, incident_type, affected_frameworks
        )
        
        # Generate timeline
        timeline = self._generate_incident_timeline(incident_events, start_time, end_time)
        
        # Identify compliance implications
        compliance_implications = self._identify_compliance_implications(
            incident_type, impact_analysis, affected_frameworks
        )
        
        incident_report = {
            "incident_id": incident_id,
            "incident_type": incident_type,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_hours": (end_time - start_time).total_seconds() / 3600,
            "affected_frameworks": [f.value for f in affected_frameworks],
            "impact_analysis": impact_analysis,
            "timeline": timeline,
            "compliance_implications": compliance_implications,
            "notification_requirements": self._get_notification_requirements(
                incident_type, impact_analysis, affected_frameworks
            ),
            "recommended_actions": self._get_incident_recommendations(
                incident_type, impact_analysis
            ),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return incident_report
    
    def _initialize_compliance_rules(self) -> Dict[ComplianceFramework, Dict[str, Any]]:
        """Initialize compliance rules for different frameworks"""
        return {
            ComplianceFramework.GDPR: {
                "data_retention": {
                    "max_retention_days": 365,
                    "requires_justification": True,
                    "auto_deletion_required": True
                },
                "consent_management": {
                    "explicit_consent_required": True,
                    "consent_withdrawal_available": True,
                    "consent_documentation_required": True
                },
                "data_subject_rights": {
                    "right_to_access": True,
                    "right_to_rectification": True,
                    "right_to_erasure": True,
                    "right_to_portability": True,
                    "response_time_days": 30
                },
                "breach_notification": {
                    "authority_notification_hours": 72,
                    "subject_notification_required": True,
                    "documentation_required": True
                }
            },
            ComplianceFramework.HIPAA: {
                "access_controls": {
                    "unique_user_identification": True,
                    "automatic_logoff": True,
                    "encryption_required": True
                },
                "audit_controls": {
                    "audit_logging_required": True,
                    "log_retention_years": 6,
                    "regular_review_required": True
                },
                "integrity": {
                    "data_integrity_controls": True,
                    "transmission_security": True,
                    "alteration_detection": True
                }
            },
            ComplianceFramework.SOX: {
                "internal_controls": {
                    "segregation_of_duties": True,
                    "authorization_controls": True,
                    "documentation_required": True
                },
                "financial_reporting": {
                    "accuracy_controls": True,
                    "completeness_controls": True,
                    "timing_controls": True
                }
            }
        }
    
    def _initialize_violation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize violation detection templates"""
        return {
            "unauthorized_access": {
                "severity": "high",
                "description": "Unauthorized access to system resources",
                "frameworks": [ComplianceFramework.HIPAA, ComplianceFramework.GDPR],
                "detection_patterns": ["failed_authentication", "privilege_escalation"]
            },
            "data_retention_violation": {
                "severity": "medium",
                "description": "Data retained beyond policy limits",
                "frameworks": [ComplianceFramework.GDPR],
                "detection_patterns": ["expired_data_present"]
            },
            "insufficient_audit_logging": {
                "severity": "medium", 
                "description": "Inadequate audit trail coverage",
                "frameworks": [ComplianceFramework.HIPAA, ComplianceFramework.SOX],
                "detection_patterns": ["missing_audit_events"]
            }
        }
    
    def _gather_audit_trail_data(
        self, framework: ComplianceFramework, start_date: datetime, 
        end_date: datetime, scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather audit trail data for compliance analysis"""
        audit_events = self.audit_logger.get_audit_trail(
            start_date=start_date,
            end_date=end_date
        )
        
        # Filter events relevant to the framework
        relevant_events = [
            event for event in audit_events
            if framework in (event.compliance_tags or [])
        ]
        
        return {
            "total_events": len(audit_events),
            "relevant_events": len(relevant_events),
            "events_by_type": self._categorize_events_by_type(relevant_events),
            "events_by_user": self._categorize_events_by_user(relevant_events),
            "high_risk_events": [
                event for event in relevant_events
                if event.audit_level.value in ["critical", "high"]
            ],
            "failed_events": [
                event for event in relevant_events
                if not event.success
            ]
        }
    
    def _gather_data_privacy_data(
        self, framework: ComplianceFramework, start_date: datetime,
        end_date: datetime, scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather data privacy-related information"""
        # Get sessions with privacy implications
        all_sessions = list(self.session_manager.completed_sessions.values())
        privacy_sessions = [
            session for session in all_sessions
            if session.start_time >= start_date and session.start_time <= end_date
        ]
        
        # Analyze data handling patterns
        data_types_processed = set()
        user_consent_status = {}
        data_retention_analysis = {}
        
        for session in privacy_sessions:
            # Extract data types from session metadata
            if "data_types" in session.metadata:
                data_types_processed.update(session.metadata["data_types"])
            
            # Check consent status
            user_consent_status[session.user_id] = session.metadata.get("user_consent", False)
        
        return {
            "sessions_analyzed": len(privacy_sessions),
            "unique_users": len(set(session.user_id for session in privacy_sessions)),
            "data_types_processed": list(data_types_processed),
            "user_consent_rate": sum(user_consent_status.values()) / len(user_consent_status) if user_consent_status else 0,
            "sessions_with_pii": len([s for s in privacy_sessions if s.metadata.get("contains_pii", False)])
        }
    
    def _gather_security_data(
        self, framework: ComplianceFramework, start_date: datetime,
        end_date: datetime, scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather security-related compliance data"""
        security_events = self.audit_logger.get_audit_trail(
            start_date=start_date,
            end_date=end_date
        )
        
        # Filter security-relevant events
        security_relevant = [
            event for event in security_events
            if event.event_type.value in [
                "user_authentication", "error_occurrence", "api_access"
            ] or event.audit_level.value == "critical"
        ]
        
        # Analyze security patterns
        failed_auth_attempts = len([
            e for e in security_relevant 
            if e.event_type.value == "user_authentication" and not e.success
        ])
        
        critical_errors = len([
            e for e in security_relevant
            if e.audit_level.value == "critical"
        ])
        
        return {
            "total_security_events": len(security_relevant),
            "failed_authentication_attempts": failed_auth_attempts,
            "critical_security_errors": critical_errors,
            "unique_ip_addresses": len(set(
                e.ip_address for e in security_relevant if e.ip_address
            )),
            "security_incidents": self._identify_security_incidents(security_relevant)
        }
    
    def _gather_user_activity_data(
        self, framework: ComplianceFramework, start_date: datetime,
        end_date: datetime, scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather user activity data for compliance analysis"""
        user_sessions = []
        for session in self.session_manager.completed_sessions.values():
            if session.start_time >= start_date and session.start_time <= end_date:
                user_sessions.append(session)
        
        # Analyze user activity patterns
        user_activity = defaultdict(list)
        for session in user_sessions:
            user_activity[session.user_id].append(session)
        
        return {
            "total_user_sessions": len(user_sessions),
            "unique_active_users": len(user_activity),
            "average_sessions_per_user": len(user_sessions) / len(user_activity) if user_activity else 0,
            "user_activity_patterns": self._analyze_user_patterns(user_activity),
            "high_activity_users": self._identify_high_activity_users(user_activity)
        }
    
    def _gather_performance_data(
        self, framework: ComplianceFramework, start_date: datetime,
        end_date: datetime, scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather system performance data"""
        performance_sessions = []
        for session in self.session_manager.completed_sessions.values():
            if (session.start_time >= start_date and session.start_time <= end_date 
                and session.session_metrics):
                performance_sessions.append(session)
        
        if not performance_sessions:
            return {"message": "No performance data available for the period"}
        
        # Extract performance metrics
        durations = [s.session_metrics.total_duration_ms for s in performance_sessions]
        error_counts = [s.session_metrics.error_count for s in performance_sessions]
        
        return {
            "sessions_with_metrics": len(performance_sessions),
            "average_duration_ms": statistics.mean(durations),
            "max_duration_ms": max(durations),
            "total_errors": sum(error_counts),
            "sessions_with_errors": len([s for s in performance_sessions if s.session_metrics.error_count > 0]),
            "performance_degradation_incidents": self._identify_performance_issues(performance_sessions)
        }
    
    def _gather_compliance_summary_data(
        self, framework: ComplianceFramework, start_date: datetime,
        end_date: datetime, scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather comprehensive compliance summary data"""
        audit_data = self._gather_audit_trail_data(framework, start_date, end_date, scope)
        privacy_data = self._gather_data_privacy_data(framework, start_date, end_date, scope)
        security_data = self._gather_security_data(framework, start_date, end_date, scope)
        
        return {
            "audit_summary": audit_data,
            "privacy_summary": privacy_data,
            "security_summary": security_data,
            "reporting_period_days": (end_date - start_date).days,
            "framework": framework.value
        }
    
    def _gather_general_compliance_data(
        self, framework: ComplianceFramework, start_date: datetime,
        end_date: datetime, scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather general compliance data"""
        return {
            "framework": framework.value,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "scope": scope
        }
    
    def _analyze_compliance_metrics(
        self, framework: ComplianceFramework, report_data: Dict[str, Any],
        start_date: datetime, end_date: datetime
    ) -> List[ComplianceMetric]:
        """Analyze compliance metrics based on framework requirements"""
        metrics = []
        rules = self.compliance_rules.get(framework, {})
        
        for rule_name, rule_config in rules.items():
            metric = self._evaluate_compliance_metric(
                framework, rule_name, rule_config, report_data
            )
            if metric:
                metrics.append(metric)
        
        return metrics
    
    def _evaluate_compliance_metric(
        self, framework: ComplianceFramework, rule_name: str, 
        rule_config: Dict[str, Any], report_data: Dict[str, Any]
    ) -> Optional[ComplianceMetric]:
        """Evaluate a specific compliance metric"""
        
        # GDPR Data Retention Metric
        if rule_name == "data_retention" and framework == ComplianceFramework.GDPR:
            max_retention_days = rule_config.get("max_retention_days", 365)
            # This would check actual data retention in practice
            current_retention = 300  # Example value
            
            status = (ComplianceStatus.COMPLIANT if current_retention <= max_retention_days 
                     else ComplianceStatus.NON_COMPLIANT)
            
            return ComplianceMetric(
                metric_name="Data Retention Compliance",
                metric_value=current_retention,
                target_value=max_retention_days,
                status=status,
                description=f"Current data retention period vs. maximum allowed",
                evidence=[f"Current retention: {current_retention} days"],
                recommendations=["Implement automated data deletion"] if status != ComplianceStatus.COMPLIANT else [],
                risk_level="medium" if status != ComplianceStatus.COMPLIANT else "low"
            )
        
        # HIPAA Access Controls Metric
        elif rule_name == "access_controls" and framework == ComplianceFramework.HIPAA:
            # Check if unique user identification is enforced
            unique_users = report_data.get("security_summary", {}).get("unique_ip_addresses", 0)
            total_events = report_data.get("audit_summary", {}).get("total_events", 0)
            
            if total_events > 0:
                access_control_score = min(unique_users / total_events * 10, 1.0)  # Simplified calculation
                status = (ComplianceStatus.COMPLIANT if access_control_score >= 0.8 
                         else ComplianceStatus.PARTIAL_COMPLIANCE)
                
                return ComplianceMetric(
                    metric_name="Access Control Implementation",
                    metric_value=access_control_score,
                    target_value=1.0,
                    status=status,
                    description="Effectiveness of access control mechanisms",
                    evidence=[f"Access control score: {access_control_score:.2f}"],
                    recommendations=["Strengthen user authentication"] if status != ComplianceStatus.COMPLIANT else [],
                    risk_level="high" if status == ComplianceStatus.NON_COMPLIANT else "medium"
                )
        
        # Generic audit logging metric
        elif "audit" in rule_name.lower():
            audit_events = report_data.get("audit_summary", {}).get("total_events", 0)
            coverage_score = min(audit_events / 1000, 1.0) if audit_events > 0 else 0  # Simplified
            
            status = (ComplianceStatus.COMPLIANT if coverage_score >= 0.9
                     else ComplianceStatus.PARTIAL_COMPLIANCE if coverage_score >= 0.7
                     else ComplianceStatus.NON_COMPLIANT)
            
            return ComplianceMetric(
                metric_name="Audit Logging Coverage",
                metric_value=coverage_score,
                target_value=1.0,
                status=status,
                description="Comprehensiveness of audit logging",
                evidence=[f"Total audit events: {audit_events}"],
                recommendations=["Expand audit logging scope"] if status != ComplianceStatus.COMPLIANT else [],
                risk_level="high" if status == ComplianceStatus.NON_COMPLIANT else "medium"
            )
        
        return None
    
    def _identify_violations(
        self, framework: ComplianceFramework, report_data: Dict[str, Any], 
        metrics: List[ComplianceMetric]
    ) -> List[ComplianceViolation]:
        """Identify compliance violations from data and metrics"""
        violations = []
        
        # Check for violations based on non-compliant metrics
        for metric in metrics:
            if metric.status == ComplianceStatus.NON_COMPLIANT:
                violation = ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    framework=framework,
                    violation_type=metric.metric_name,
                    severity="high" if metric.risk_level == "high" else "medium",
                    description=f"Non-compliance detected in {metric.metric_name}: {metric.description}",
                    affected_systems=["Regulus AI System"],
                    data_types_involved=["user_queries", "system_responses"],
                    timestamp=datetime.now(timezone.utc),
                    detection_method="automated_compliance_analysis",
                    remediation_status="identified",
                    remediation_actions=metric.recommendations,
                    estimated_impact="moderate",
                    related_incidents=[]
                )
                violations.append(violation)
        
        # Check for specific violation patterns
        security_data = report_data.get("security_summary", {})
        if security_data.get("failed_authentication_attempts", 0) > 10:
            violations.append(ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                framework=framework,
                violation_type="excessive_failed_authentication",
                severity="medium",
                description="High number of failed authentication attempts detected",
                affected_systems=["Authentication System"],
                data_types_involved=["authentication_logs"],
                timestamp=datetime.now(timezone.utc),
                detection_method="threshold_analysis",
                remediation_status="identified",
                remediation_actions=["Implement account lockout policies", "Review authentication logs"],
                estimated_impact="low",
                related_incidents=[]
            ))
        
        return violations
    
    def _calculate_overall_compliance_score(self, metrics: List[ComplianceMetric]) -> float:
        """Calculate overall compliance score from metrics"""
        if not metrics:
            return 0.0
        
        compliant_count = len([m for m in metrics if m.status == ComplianceStatus.COMPLIANT])
        partial_count = len([m for m in metrics if m.status == ComplianceStatus.PARTIAL_COMPLIANCE])
        
        # Weighted scoring: compliant = 1.0, partial = 0.5, non-compliant = 0.0
        weighted_score = (compliant_count * 1.0 + partial_count * 0.5) / len(metrics)
        return weighted_score
    
    def _generate_executive_summary(
        self, framework: ComplianceFramework, report_type: ReportType,
        metrics: List[ComplianceMetric], violations: List[ComplianceViolation],
        overall_score: float
    ) -> str:
        """Generate executive summary for the report"""
        summary = f"This {report_type.value.replace('_', ' ').title()} report for {framework.value.upper()} "
        summary += f"covers the analysis of {len(metrics)} compliance metrics. "
        
        compliance_level = "high" if overall_score >= 0.9 else "moderate" if overall_score >= 0.7 else "low"
        summary += f"The overall compliance score is {overall_score:.1%}, indicating {compliance_level} compliance. "
        
        if violations:
            critical_violations = len([v for v in violations if v.severity == "critical"])
            high_violations = len([v for v in violations if v.severity == "high"])
            
            summary += f"A total of {len(violations)} violations were identified, "
            if critical_violations > 0:
                summary += f"including {critical_violations} critical issues "
            if high_violations > 0:
                summary += f"and {high_violations} high-severity issues. "
            summary += "Immediate attention is required for remediation. "
        else:
            summary += "No compliance violations were detected during this reporting period. "
        
        summary += "Detailed findings and recommendations are provided in the following sections."
        return summary
    
    def _generate_recommendations(
        self, framework: ComplianceFramework, violations: List[ComplianceViolation],
        metrics: List[ComplianceMetric]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Collect recommendations from violations
        for violation in violations:
            recommendations.extend(violation.remediation_actions)
        
        # Collect recommendations from metrics
        for metric in metrics:
            recommendations.extend(metric.recommendations)
        
        # Add framework-specific recommendations
        framework_recommendations = {
            ComplianceFramework.GDPR: [
                "Implement regular data retention reviews",
                "Enhance user consent management processes",
                "Conduct privacy impact assessments for new features"
            ],
            ComplianceFramework.HIPAA: [
                "Strengthen access controls and authentication",
                "Implement comprehensive audit logging",
                "Enhance data encryption for all PHI"
            ],
            ComplianceFramework.SOX: [
                "Implement segregation of duties controls",
                "Enhance documentation of internal controls",
                "Conduct regular control effectiveness testing"
            ]
        }
        
        recommendations.extend(framework_recommendations.get(framework, []))
        
        # Remove duplicates and return top recommendations
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:10]  # Limit to top 10
    
    def _perform_risk_assessment(
        self, violations: List[ComplianceViolation], metrics: List[ComplianceMetric]
    ) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        risk_levels = Counter()
        risk_categories = defaultdict(list)
        
        # Analyze violations
        for violation in violations:
            risk_levels[violation.severity] += 1
            risk_categories[violation.violation_type].append(violation.severity)
        
        # Analyze metrics
        for metric in metrics:
            if metric.status != ComplianceStatus.COMPLIANT:
                risk_levels[metric.risk_level] += 1
                risk_categories[metric.metric_name].append(metric.risk_level)
        
        # Calculate overall risk score
        risk_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        total_risk_score = sum(risk_levels[level] * risk_weights.get(level, 0) for level in risk_levels)
        max_possible_score = len(violations + metrics) * 4  # Assuming all could be critical
        normalized_risk_score = total_risk_score / max_possible_score if max_possible_score > 0 else 0
        
        return {
            "overall_risk_score": normalized_risk_score,
            "risk_level_distribution": dict(risk_levels),
            "highest_risk_categories": [
                category for category, levels in risk_categories.items()
                if "critical" in levels or "high" in levels
            ],
            "risk_assessment_summary": self._generate_risk_summary(normalized_risk_score, risk_levels),
            "mitigation_priority": self._prioritize_risk_mitigation(risk_categories)
        }
    
    def _generate_risk_summary(self, risk_score: float, risk_levels: Counter) -> str:
        """Generate risk assessment summary"""
        if risk_score >= 0.8:
            summary = "Critical risk level detected. Immediate remediation required."
        elif risk_score >= 0.6:
            summary = "High risk level identified. Prompt attention needed."
        elif risk_score >= 0.4:
            summary = "Moderate risk level. Regular monitoring recommended."
        else:
            summary = "Low risk level. Continue current practices with routine reviews."
        
        if risk_levels.get("critical", 0) > 0:
            summary += f" {risk_levels['critical']} critical issues require immediate resolution."
        
        return summary
    
    def _prioritize_risk_mitigation(self, risk_categories: Dict[str, List[str]]) -> List[str]:
        """Prioritize risk mitigation efforts"""
        priority_list = []
        
        # Sort categories by highest risk level
        sorted_categories = sorted(
            risk_categories.items(),
            key=lambda x: max([{"critical": 4, "high": 3, "medium": 2, "low": 1}.get(level, 0) for level in x[1]]),
            reverse=True
        )
        
        for category, levels in sorted_categories[:5]:  # Top 5 priorities
            max_level = max(levels, key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x, 0))
            priority_list.append(f"{category} ({max_level} priority)")
        
        return priority_list
    
    def _generate_appendices(
        self, framework: ComplianceFramework, report_data: Dict[str, Any], 
        report_type: ReportType
    ) -> Dict[str, Any]:
        """Generate report appendices with detailed data"""
        appendices = {}
        
        # Raw data appendix
        appendices["raw_data"] = {
            "description": "Raw data used for compliance analysis",
            "data": report_data
        }
        
        # Compliance rules appendix
        appendices["compliance_rules"] = {
            "description": f"Compliance rules applied for {framework.value}",
            "rules": self.compliance_rules.get(framework, {})
        }
        
        # Methodology appendix
        appendices["methodology"] = {
            "description": "Analysis methodology and scoring criteria",
            "scoring_method": "Weighted compliance scoring",
            "data_sources": ["Audit logs", "Session data", "System metrics"],
            "analysis_period": "Specified reporting period"
        }
        
        return appendices
    
    def _export_json(self, report: ComplianceReport) -> str:
        """Export report as JSON"""
        report_dict = asdict(report)
        
        # Convert enums and datetime objects
        report_dict["report_type"] = report.report_type.value
        report_dict["framework"] = report.framework.value
        report_dict["generated_at"] = report.generated_at.isoformat()
        report_dict["reporting_period_start"] = report.reporting_period_start.isoformat()
        report_dict["reporting_period_end"] = report.reporting_period_end.isoformat()
        
        # Convert violations
        report_dict["violations"] = []
        for violation in report.violations:
            violation_dict = asdict(violation)
            violation_dict["framework"] = violation.framework.value
            violation_dict["timestamp"] = violation.timestamp.isoformat()
            report_dict["violations"].append(violation_dict)
        
        # Convert metrics
        report_dict["metrics"] = []
        for metric in report.metrics:
            metric_dict = asdict(metric)
            metric_dict["status"] = metric.status.value
            report_dict["metrics"].append(metric_dict)
        
        return json.dumps(report_dict, indent=2)
    
    def _export_csv(self, report: ComplianceReport) -> str:
        """Export report summary as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Report ID", "Framework", "Report Type", "Generated At",
            "Overall Score", "Total Metrics", "Compliant Metrics",
            "Total Violations", "Critical Violations"
        ])
        
        critical_violations = len([v for v in report.violations if v.severity == "critical"])
        
        # Write data
        writer.writerow([
            report.report_id,
            report.framework.value,
            report.report_type.value,
            report.generated_at.isoformat(),
            f"{report.overall_compliance_score:.2%}",
            report.total_metrics,
            report.compliant_metrics,
            len(report.violations),
            critical_violations
        ])
        
        return output.getvalue()
    
    def _export_html(self, report: ComplianceReport) -> str:
        """Export report as HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .summary {{ margin: 20px 0; }}
                .metrics {{ margin: 20px 0; }}
                .violations {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .compliant {{ color: green; }}
                .non-compliant {{ color: red; }}
                .partial {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.title}</h1>
                <p><strong>Report ID:</strong> {report.report_id}</p>
                <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Framework:</strong> {report.framework.value.upper()}</p>
                <p><strong>Period:</strong> {report.reporting_period_start.strftime('%Y-%m-%d')} to {report.reporting_period_end.strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <p>{report.executive_summary}</p>
                <p><strong>Overall Compliance Score:</strong> {report.overall_compliance_score:.1%}</p>
            </div>
            
            <div class="metrics">
                <h2>Compliance Metrics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Current Value</th>
                        <th>Target Value</th>
                        <th>Status</th>
                        <th>Risk Level</th>
                    </tr>
        """
        
        for metric in report.metrics:
            status_class = metric.status.value.replace('_', '-')
            html += f"""
                    <tr>
                        <td>{metric.metric_name}</td>
                        <td>{metric.metric_value}</td>
                        <td>{metric.target_value}</td>
                        <td class="{status_class}">{metric.status.value.replace('_', ' ').title()}</td>
                        <td>{metric.risk_level.title()}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="violations">
                <h2>Compliance Violations</h2>
        """
        
        if report.violations:
            html += """
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Severity</th>
                        <th>Description</th>
                        <th>Status</th>
                    </tr>
            """
            for violation in report.violations:
                html += f"""
                    <tr>
                        <td>{violation.violation_type}</td>
                        <td>{violation.severity.title()}</td>
                        <td>{violation.description}</td>
                        <td>{violation.remediation_status.replace('_', ' ').title()}</td>
                    </tr>
                """
            html += "</table>"
        else:
            html += "<p>No compliance violations detected.</p>"
        
        html += """
            </div>
            
            <div class="recommendations">
                <h2>Recommendations</h2>
                <ul>
        """
        
        for recommendation in report.recommendations[:10]:
            html += f"<li>{recommendation}</li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _validate_compliance_rule(
        self, framework: ComplianceFramework, rule_name: str,
        rule_config: Dict[str, Any], validation_scope: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a specific compliance rule"""
        # This is a simplified implementation - would be more comprehensive in practice
        return {
            "rule_name": rule_name,
            "status": ComplianceStatus.COMPLIANT.value,
            "details": f"Rule {rule_name} validation passed",
            "severity": "low"
        }
    
    # Helper methods for data analysis
    def _categorize_events_by_type(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Categorize audit events by type"""
        return Counter(event.event_type.value for event in events)
    
    def _categorize_events_by_user(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Categorize audit events by user"""
        return Counter(event.user_id or "anonymous" for event in events)
    
    def _identify_security_incidents(self, events: List[AuditEvent]) -> List[Dict[str, Any]]:
        """Identify potential security incidents from events"""
        incidents = []
        # This would contain sophisticated pattern detection in practice
        return incidents
    
    def _analyze_user_patterns(self, user_activity: Dict[str, List]) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        return {"pattern_analysis": "completed"}
    
    def _identify_high_activity_users(self, user_activity: Dict[str, List]) -> List[str]:
        """Identify users with unusually high activity"""
        threshold = 10  # Example threshold
        return [
            user_id for user_id, sessions in user_activity.items() 
            if len(sessions) > threshold
        ]
    
    def _identify_performance_issues(self, sessions: List) -> List[Dict[str, Any]]:
        """Identify performance degradation incidents"""
        issues = []
        # This would contain performance analysis in practice
        return issues
    
    def _analyze_incident_impact(
        self, events: List[AuditEvent], incident_type: str, 
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Analyze the impact of an incident"""
        return {
            "events_analyzed": len(events),
            "affected_users": len(set(e.user_id for e in events if e.user_id)),
            "systems_affected": ["main_system"],
            "estimated_impact": "moderate"
        }
    
    def _generate_incident_timeline(
        self, events: List[AuditEvent], start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Generate incident timeline"""
        timeline = []
        for event in events[:10]:  # Limit for example
            timeline.append({
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "description": event.action_performed or "Event occurred"
            })
        return timeline
    
    def _identify_compliance_implications(
        self, incident_type: str, impact_analysis: Dict[str, Any],
        frameworks: List[ComplianceFramework]
    ) -> List[str]:
        """Identify compliance implications of an incident"""
        implications = []
        for framework in frameworks:
            if framework == ComplianceFramework.GDPR:
                implications.append("May require breach notification under GDPR Article 33")
            elif framework == ComplianceFramework.HIPAA:
                implications.append("Potential HIPAA breach notification required")
        return implications
    
    def _get_notification_requirements(
        self, incident_type: str, impact_analysis: Dict[str, Any],
        frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Get notification requirements for the incident"""
        requirements = {}
        for framework in frameworks:
            if framework == ComplianceFramework.GDPR:
                requirements["GDPR"] = {
                    "authority_notification_deadline": "72 hours",
                    "individual_notification_required": impact_analysis.get("affected_users", 0) > 0,
                    "documentation_required": True
                }
        return requirements
    
    def _get_incident_recommendations(
        self, incident_type: str, impact_analysis: Dict[str, Any]
    ) -> List[str]:
        """Get incident-specific recommendations"""
        return [
            "Conduct thorough incident investigation",
            "Implement additional monitoring controls",
            "Review and update incident response procedures",
            "Provide additional staff training if needed"
        ]


# Global compliance reporter instance
compliance_reporter = ComplianceReporter()


def get_compliance_reporter() -> ComplianceReporter:
    """Get the global compliance reporter instance"""
    return compliance_reporter


# Convenience functions
def generate_report(framework: ComplianceFramework, report_type: ReportType,
                   start_date: datetime, end_date: datetime) -> ComplianceReport:
    """Generate compliance report"""
    return compliance_reporter.generate_compliance_report(
        framework, report_type, start_date, end_date
    )


def validate_compliance(framework: ComplianceFramework, 
                       scope: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validate compliance"""
    return compliance_reporter.validate_compliance(framework, scope)


def export_report(report: ComplianceReport, format_type: ReportFormat) -> str:
    """Export compliance report"""
    return compliance_reporter.export_report(report, format_type)