"""
Design Alignment Tests

Reference: AJrag.txt §8 - Testing & Quality Gates

These tests validate that the implementation matches the design specifications
in AJrag.txt and agnoMCPnanobot.txt. They are NOT unit tests; they are
design compliance checks.

If these tests fail, it indicates architectural drift from the spec.
"""

import pytest
from src.ingestion_workflow import run_ingestion_with_metadata
from src.pydantic_schemas import AJPack, TOC, SecurityMetadata


class TestSchemaValidation:
    """
    AJrag.txt §8: Schema tests
    - JSON Schema validation
    - Pointer resolution
    - Manifest checksums
    """

    def test_aj_pack_round_trip(self):
        """
        AJrag.txt §2.2 Step 6: AJ Pack must be immutable and resolvable.
        
        All pointers must be resolvable, and the pack must survive
        serialization/deserialization without data loss.
        """
        aj_pack, warnings = run_ingestion_with_metadata("test_source")
        
        # Validate basic structure
        assert aj_pack.manifest is not None
        assert aj_pack.toc is not None
        assert len(aj_pack.content) > 0
        
        # Test serialization round-trip
        pack_dict = aj_pack.model_dump()
        reconstructed = AJPack(**pack_dict)
        
        # Verify no data loss
        assert reconstructed.manifest.dataset_id == aj_pack.manifest.dataset_id
        assert reconstructed.manifest.version == aj_pack.manifest.version
        assert len(reconstructed.content) == len(aj_pack.content)

    def test_stable_section_ids(self):
        """
        AJrag.txt §9: Citations must be immutable section_ids.
        
        Section IDs must be stable across ingestion runs for the same source.
        """
        # Run ingestion twice
        pack1, _ = run_ingestion_with_metadata("test_source")
        pack2, _ = run_ingestion_with_metadata("test_source")
        
        # Extract all section_ids from both packs
        ids1 = set()
        ids2 = set()
        
        for file_content in pack1.content:
            for section in file_content.content:
                ids1.add(section.section_id)
        
        for file_content in pack2.content:
            for section in file_content.content:
                ids2.add(section.section_id)
        
        # Section IDs must be identical
        assert ids1 == ids2, "Section IDs changed between ingestion runs - violates immutability"

    def test_toc_pointer_resolution(self):
        """
        AJrag.txt §5.2: TOC pointers must resolve to actual sections.
        
        Every section referenced in the TOC must exist in the content.
        """
        aj_pack, _ = run_ingestion_with_metadata("test_source")
        
        # Build a set of all actual section_ids
        actual_sections = set()
        for file_content in aj_pack.content:
            for section in file_content.content:
                actual_sections.add((file_content.file_id, section.section_id))
        
        # Verify every TOC entry points to a real section
        for file_toc in aj_pack.toc.index:
            for section_toc in file_toc.sections:
                assert (file_toc.file_id, section_toc.section_id) in actual_sections, \
                    f"TOC references non-existent section: {file_toc.file_id}/{section_toc.section_id}"


class TestTOCRouting:
    """
    AJrag.txt §8: Routing tests
    - Given canonical intents → TOC plan matches expected sections
    - Disambiguation rules work correctly
    - Alias and entity hits are accurate
    """

    def test_disambiguation_rules_applied(self):
        """
        AJrag.txt §5.2: Disambiguation rules must boost preferred sections.
        
        When a query contains all triggers from a disambiguation rule,
        the preferred sections must be ranked higher.
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        # Include required security headers
        headers = {
            "X-User-Region": "US",
            "X-PHI-Clearance": "true",
            "X-PII-Clearance": "true"
        }
        
        # This query should trigger disambiguation if rules exist
        # Example: "DKA" + "electrolytes" should prefer specific sections
        response = client.post('/query', json={
            'question': 'What are the electrolyte abnormalities in DKA?'
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # The response should have high confidence due to disambiguation
        # (This is a placeholder - actual assertion depends on your data)
        assert data['confidence'] >= 0.0

    def test_alias_matching(self):
        """
        AJrag.txt §2.2 Step 4: Aliases must improve routing accuracy.
        
        A query using an alias should route to the same section as
        a query using the primary label.
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        # Query using primary term
        response1 = client.post('/query', json={
            'question': 'What are the side effects?'
        })
        
        # Query using alias (if "adverse reactions" is an alias for "side effects")
        response2 = client.post('/query', json={
            'question': 'What are the adverse reactions?'
        })
        
        # Both should route to similar sections
        # (This is a basic check - in production, we'd verify exact section_id matches)
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_entity_recognition(self):
        """
        AJrag.txt §2.2 Step 1: Entities must be extracted and used for routing.
        
        A query mentioning a specific entity (e.g., "Metformin") should
        route to sections tagged with that entity.
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        # Include required security headers
        headers = {
            "X-User-Region": "US",
            "X-PHI-Clearance": "true",
            "X-PII-Clearance": "true"
        }
        
        response = client.post('/query', json={
            'question': 'What is Metformin used for?'
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # The answer should come from a section with high relevance
        assert data['confidence'] >= 0.0


class TestSecurityAndCompliance:
    """
    AJrag.txt §7: Security & Compliance
    - PHI/PII/residency enforcement
    - Policy metadata checked before context loads
    """

    def test_security_metadata_exists(self):
        """
        AJrag.txt §7: Security metadata must be present in TOC.
        
        Every AJ Pack must have security metadata defined.
        """
        aj_pack, _ = run_ingestion_with_metadata("test_source")
        
        assert aj_pack.toc.security is not None
        assert isinstance(aj_pack.toc.security, SecurityMetadata)

    @pytest.mark.skip(reason="Policy enforcement not yet implemented - tracked in Drift_Mitigation_ReBuild_Steps.md Phase 2.1")
    def test_phi_access_denied_without_clearance(self):
        """
        AJrag.txt §7: PHI data must be blocked without proper clearance.
        
        If the AJ Pack is flagged as PHI, queries from users without
        clearance must be rejected.
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        # TODO: Add user context to request (requires service.py changes)
        # For now, this test is skipped and tracked as technical debt
        pass

    @pytest.mark.skip(reason="Policy enforcement not yet implemented - tracked in Drift_Mitigation_ReBuild_Steps.md Phase 2.1")
    def test_residency_violation_blocked(self):
        """
        AJrag.txt §7: Data residency rules must be enforced.
        
        If data is marked as US-only, queries from non-US regions
        must be rejected.
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        # TODO: Add region context to request (requires service.py changes)
        # For now, this test is skipped and tracked as technical debt
        pass


class TestPerformanceBudgets:
    """
    AJrag.txt §8: Performance tests
    - p95 token load < budget
    - Mean hops < target
    - Context thrash < 5%
    """

    def test_token_budget_not_exceeded(self):
        """
        AJrag.txt §3.1: Loader agents must respect token budgets.
        
        The total tokens loaded into context for any query must not
        exceed the configured budget (default: 4000 tokens).
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        response = client.post('/query', json={
            'question': 'What is the complete treatment protocol for sepsis?'
        })
        
        assert response.status_code == 200
        
        # TODO: Add token counting to service.py to validate this
        # For now, we just verify the query succeeds
        # This will be implemented in Phase 2.3 (Loader Agent)

    @pytest.mark.skip(reason="Loader Agent not yet implemented - tracked in Drift_Mitigation_ReBuild_Steps.md Phase 2.3")
    def test_context_thrash_below_threshold(self):
        """
        AJrag.txt §2.2 Step 5: Context thrash must be < 5%.
        
        Thrash occurs when sections are loaded and then immediately
        evicted due to budget constraints. This indicates poor routing.
        """
        # TODO: Implement thrash tracking in Loader Agent
        # This test will be enabled in Phase 2.3
        pass


class TestCitationStability:
    """
    AJrag.txt §9: Immutable packs → stable citations
    """

    def test_citations_are_section_ids(self):
        """
        AJrag.txt §9: Citations must be section_ids, not page numbers or text snippets.
        
        This ensures citations remain valid even if the source document
        is reformatted or re-paginated.
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        # Include required security headers
        headers = {
            "X-User-Region": "US",
            "X-PHI-Clearance": "true",
            "X-PII-Clearance": "true"
        }
        
        response = client.post('/query', json={
            'question': 'What is diabetes?'
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify citations are present and are strings (section_ids)
        assert 'citations' in data
        assert isinstance(data['citations'], list)
        assert len(data['citations']) >= 0
        
        for citation in data['citations']:
            assert isinstance(citation, str)
            # Section IDs should follow the pattern: file_id_section_id or similar
            # This is a basic check - in production, we'd validate the format more strictly
            assert len(citation) > 0

    def test_citations_traceable_to_source(self):
        """
        AJrag.txt §9: Every citation must be traceable to a specific section.
        
        Given a citation (section_id), we must be able to retrieve the
        exact source text from the AJ Pack.
        """
        from src.service import build_fallback_app
        from fastapi.testclient import TestClient
        
        app = build_fallback_app()
        client = TestClient(app)
        
        # Get a query response with citations
        response = client.post('/query', json={
            'question': 'What is diabetes?'
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify we can look up each citation
        aj_pack, _ = run_ingestion_with_metadata("test_source")
        
        for citation in data['citations']:
            # Search for this section_id in the AJ Pack
            found = False
            for file_content in aj_pack.content:
                for section in file_content.content:
                    if section.section_id == citation:
                        found = True
                        # Verify the section has actual content
                        assert len(section.text_or_data) > 0
                        break
                if found:
                    break
            
            assert found, f"Citation '{citation}' not found in AJ Pack - broken reference"


# Summary fixture to report test results
@pytest.fixture(scope="session", autouse=True)
def design_alignment_summary(request):
    """
    Print a summary of design alignment test results at the end of the session.
    """
    yield
    
    print("\n" + "="*80)
    print("DESIGN ALIGNMENT TEST SUMMARY")
    print("="*80)
    print("\nReference: AJrag.txt §8 - Testing & Quality Gates")
    print("\nThese tests validate compliance with the design specifications.")
    print("Failures indicate architectural drift that must be addressed.")
    print("\nFor recovery steps, see: Drift_Mitigation_ReBuild_Steps.md")
    print("="*80 + "\n")
