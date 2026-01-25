"""
Policy Enforcement Module

Reference: AJrag.txt §7 - Security & Compliance

This module enforces security policies defined in AJ Pack metadata before
allowing context loads or query processing.

Key Features:
- PHI/PII access control
- Data residency enforcement
- Compliance audit trail
"""

from typing import Tuple
from .pydantic_schemas import SecurityMetadata


class PolicyEnforcer:
    """
    Enforces security policies defined in AJ Pack metadata.
    
    Reference: AJrag.txt §7 - "Residency & access baked into TOC metadata;
    loader enforces before every load."
    
    This class checks:
    1. Data residency requirements (e.g., US-only, EU-only)
    2. PHI/PII access clearance
    3. Any custom policy flags in the metadata
    """
    
    def __init__(self, security_metadata: SecurityMetadata):
        """
        Initialize the policy enforcer with security metadata from the AJ Pack.
        
        Args:
            security_metadata: The SecurityMetadata from the AJ Pack's TOC
        """
        self.metadata = security_metadata
    
    def check_residency(self, user_region: str) -> bool:
        """
        Check if the user's region is allowed to access this data.
        
        Reference: AJrag.txt §7 - "Residency baked into TOC metadata"
        
        Args:
            user_region: The user's geographic region (e.g., "US", "EU", "APAC")
        
        Returns:
            True if access is allowed, False otherwise
        """
        # If no residency requirement, allow all regions
        if not self.metadata.residency:
            return True
        
        # If residency is specified, user must be in that region
        return user_region.upper() == self.metadata.residency.upper()
    
    def check_phi_access(self, user_has_phi_clearance: bool) -> bool:
        """
        Check if the user is cleared to access PHI (Protected Health Information).
        
        Reference: AJrag.txt §7 - "PII/PHI tags prevent accidental context loading"
        
        Args:
            user_has_phi_clearance: Whether the user has PHI access clearance
        
        Returns:
            True if access is allowed, False otherwise
        """
        # If data is not PHI, allow access
        if not self.metadata.phi:
            return True
        
        # If data is PHI, user must have clearance
        return user_has_phi_clearance
    
    def check_pii_access(self, user_has_pii_clearance: bool) -> bool:
        """
        Check if the user is cleared to access PII (Personally Identifiable Information).
        
        Reference: AJrag.txt §7 - "PII/PHI tags prevent accidental context loading"
        
        Args:
            user_has_pii_clearance: Whether the user has PII access clearance
        
        Returns:
            True if access is allowed, False otherwise
        """
        # If data is not PII, allow access
        if not self.metadata.pii:
            return True
        
        # If data is PII, user must have clearance
        return user_has_pii_clearance
    
    def enforce(
        self,
        user_region: str = "UNKNOWN",
        user_has_phi_clearance: bool = False,
        user_has_pii_clearance: bool = False
    ) -> Tuple[bool, str]:
        """
        Enforce all security policies.
        
        This is the main entry point for policy enforcement. It checks all
        policies and returns a single decision.
        
        Reference: AJrag.txt §7 - "Loader enforces before every load"
        
        Args:
            user_region: The user's geographic region
            user_has_phi_clearance: Whether the user has PHI access clearance
            user_has_pii_clearance: Whether the user has PII access clearance
        
        Returns:
            A tuple of (allowed: bool, reason: str)
            - If allowed is True, reason is "Access granted."
            - If allowed is False, reason explains why access was denied
        """
        # Check residency first (most restrictive)
        if not self.check_residency(user_region):
            return False, (
                f"Data residency violation. This data is restricted to "
                f"{self.metadata.residency} region. User is in {user_region} region."
            )
        
        # Check PHI access
        if not self.check_phi_access(user_has_phi_clearance):
            return False, (
                "PHI access denied. This data contains Protected Health Information "
                "and requires appropriate clearance."
            )
        
        # Check PII access
        if not self.check_pii_access(user_has_pii_clearance):
            return False, (
                "PII access denied. This data contains Personally Identifiable Information "
                "and requires appropriate clearance."
            )
        
        # All checks passed
        return True, "Access granted."
    
    def get_policy_summary(self) -> dict:
        """
        Get a summary of the active policies for this AJ Pack.
        
        Useful for logging and audit trails.
        
        Returns:
            A dictionary describing the active policies
        """
        return {
            "residency_required": self.metadata.residency,
            "phi_protected": self.metadata.phi,
            "pii_protected": self.metadata.pii,
            "enforcement_level": self._calculate_enforcement_level()
        }
    
    def _calculate_enforcement_level(self) -> str:
        """
        Calculate the overall enforcement level based on active policies.
        
        Returns:
            "strict" if PHI/PII or residency is enforced
            "moderate" if only one policy is active
            "permissive" if no policies are active
        """
        active_policies = sum([
            bool(self.metadata.residency),
            self.metadata.phi,
            self.metadata.pii
        ])
        
        if active_policies >= 2:
            return "strict"
        elif active_policies == 1:
            return "moderate"
        else:
            return "permissive"


class PolicyViolationError(Exception):
    """
    Exception raised when a policy violation is detected.
    
    This can be used in production code to handle policy violations
    with proper error handling and logging.
    """
    
    def __init__(self, reason: str, policy_summary: dict):
        self.reason = reason
        self.policy_summary = policy_summary
        super().__init__(f"Policy violation: {reason}")
