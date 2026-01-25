"""
Policy Enforcement Tests

Reference: AJrag.txt §7 - Security & Compliance

These tests validate that the PolicyEnforcer correctly enforces
security policies defined in AJ Pack metadata.
"""

import pytest
from src.policy_enforcer import PolicyEnforcer, PolicyViolationError
from src.pydantic_schemas import SecurityMetadata


class TestPolicyEnforcer:
    """Test the PolicyEnforcer class."""

    def test_permissive_policy_allows_all(self):
        """
        When no security policies are active, all access should be allowed.
        """
        metadata = SecurityMetadata(residency=None, pii=False, phi=False)
        enforcer = PolicyEnforcer(metadata)
        
        allowed, reason = enforcer.enforce(
            user_region="UNKNOWN",
            user_has_phi_clearance=False,
            user_has_pii_clearance=False
        )
        
        assert allowed is True
        assert reason == "Access granted."

    def test_residency_enforcement_blocks_wrong_region(self):
        """
        AJrag.txt §7: Data residency rules must be enforced.
        
        If data is marked as US-only, queries from non-US regions
        must be rejected.
        """
        metadata = SecurityMetadata(residency="US", pii=False, phi=False)
        enforcer = PolicyEnforcer(metadata)
        
        # User from EU should be blocked
        allowed, reason = enforcer.enforce(
            user_region="EU",
            user_has_phi_clearance=False,
            user_has_pii_clearance=False
        )
        
        assert allowed is False
        assert "residency violation" in reason.lower()
        assert "US" in reason
        assert "EU" in reason

    def test_residency_enforcement_allows_correct_region(self):
        """
        Users in the correct region should be allowed access.
        """
        metadata = SecurityMetadata(residency="US", pii=False, phi=False)
        enforcer = PolicyEnforcer(metadata)
        
        # User from US should be allowed
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=False,
            user_has_pii_clearance=False
        )
        
        assert allowed is True
        assert reason == "Access granted."

    def test_residency_check_is_case_insensitive(self):
        """
        Region codes should be case-insensitive.
        """
        metadata = SecurityMetadata(residency="US", pii=False, phi=False)
        enforcer = PolicyEnforcer(metadata)
        
        # Lowercase "us" should work
        allowed, _ = enforcer.enforce(user_region="us")
        assert allowed is True
        
        # Mixed case should work
        allowed, _ = enforcer.enforce(user_region="Us")
        assert allowed is True

    def test_phi_enforcement_blocks_without_clearance(self):
        """
        AJrag.txt §7: PHI data must be blocked without proper clearance.
        
        If the AJ Pack is flagged as PHI, queries from users without
        clearance must be rejected.
        """
        metadata = SecurityMetadata(residency=None, pii=False, phi=True)
        enforcer = PolicyEnforcer(metadata)
        
        # User without PHI clearance should be blocked
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=False,
            user_has_pii_clearance=False
        )
        
        assert allowed is False
        assert "phi" in reason.lower()
        assert "clearance" in reason.lower()

    def test_phi_enforcement_allows_with_clearance(self):
        """
        Users with PHI clearance should be allowed access to PHI data.
        """
        metadata = SecurityMetadata(residency=None, pii=False, phi=True)
        enforcer = PolicyEnforcer(metadata)
        
        # User with PHI clearance should be allowed
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=True,
            user_has_pii_clearance=False
        )
        
        assert allowed is True
        assert reason == "Access granted."

    def test_pii_enforcement_blocks_without_clearance(self):
        """
        PII data must be blocked without proper clearance.
        """
        metadata = SecurityMetadata(residency=None, pii=True, phi=False)
        enforcer = PolicyEnforcer(metadata)
        
        # User without PII clearance should be blocked
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=False,
            user_has_pii_clearance=False
        )
        
        assert allowed is False
        assert "pii" in reason.lower()
        assert "clearance" in reason.lower()

    def test_pii_enforcement_allows_with_clearance(self):
        """
        Users with PII clearance should be allowed access to PII data.
        """
        metadata = SecurityMetadata(residency=None, pii=True, phi=False)
        enforcer = PolicyEnforcer(metadata)
        
        # User with PII clearance should be allowed
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=False,
            user_has_pii_clearance=True
        )
        
        assert allowed is True
        assert reason == "Access granted."

    def test_multiple_policies_all_must_pass(self):
        """
        When multiple policies are active, ALL must be satisfied.
        
        This tests the "strict" enforcement level.
        """
        metadata = SecurityMetadata(residency="US", pii=True, phi=True)
        enforcer = PolicyEnforcer(metadata)
        
        # User with correct region but no clearances - should fail
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=False,
            user_has_pii_clearance=False
        )
        assert allowed is False
        
        # User with PHI clearance but not PII - should fail
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=True,
            user_has_pii_clearance=False
        )
        assert allowed is False
        
        # User with all clearances - should pass
        allowed, reason = enforcer.enforce(
            user_region="US",
            user_has_phi_clearance=True,
            user_has_pii_clearance=True
        )
        assert allowed is True

    def test_policy_summary_reflects_active_policies(self):
        """
        The policy summary should accurately reflect which policies are active.
        """
        metadata = SecurityMetadata(residency="EU", pii=True, phi=False)
        enforcer = PolicyEnforcer(metadata)
        
        summary = enforcer.get_policy_summary()
        
        assert summary["residency_required"] == "EU"
        assert summary["pii_protected"] is True
        assert summary["phi_protected"] is False
        assert summary["enforcement_level"] == "strict"  # 2 policies active

    def test_enforcement_level_calculation(self):
        """
        Test that enforcement levels are calculated correctly.
        """
        # Permissive: no policies
        metadata = SecurityMetadata(residency=None, pii=False, phi=False)
        enforcer = PolicyEnforcer(metadata)
        assert enforcer.get_policy_summary()["enforcement_level"] == "permissive"
        
        # Moderate: 1 policy
        metadata = SecurityMetadata(residency="US", pii=False, phi=False)
        enforcer = PolicyEnforcer(metadata)
        assert enforcer.get_policy_summary()["enforcement_level"] == "moderate"
        
        # Strict: 2+ policies
        metadata = SecurityMetadata(residency="US", pii=True, phi=False)
        enforcer = PolicyEnforcer(metadata)
        assert enforcer.get_policy_summary()["enforcement_level"] == "strict"

    def test_policy_violation_error(self):
        """
        Test that PolicyViolationError can be raised with proper context.
        """
        metadata = SecurityMetadata(residency="US", pii=True, phi=True)
        enforcer = PolicyEnforcer(metadata)
        
        try:
            allowed, reason = enforcer.enforce(user_region="EU")
            if not allowed:
                raise PolicyViolationError(reason, enforcer.get_policy_summary())
        except PolicyViolationError as e:
            assert "residency violation" in e.reason.lower()
            assert e.policy_summary["residency_required"] == "US"
            assert "Policy violation" in str(e)


class TestPolicyEnforcementIntegration:
    """
    Integration tests that verify policy enforcement works with the service.
    """

    def test_policy_enforcer_integrates_with_aj_pack(self):
        """
        Verify that PolicyEnforcer can be instantiated from a real AJ Pack.
        """
        from src.ingestion_workflow import run_ingestion_with_metadata
        
        aj_pack, _ = run_ingestion_with_metadata("test_source")
        
        # Should be able to create enforcer from AJ Pack metadata
        enforcer = PolicyEnforcer(aj_pack.toc.security)
        
        # Should be able to get policy summary
        summary = enforcer.get_policy_summary()
        assert "enforcement_level" in summary
        
        # Should be able to enforce policies
        allowed, reason = enforcer.enforce(user_region="US")
        assert isinstance(allowed, bool)
        assert isinstance(reason, str)
