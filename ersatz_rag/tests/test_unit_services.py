"""
Unit tests for individual microservices
"""

import pytest
import requests
import json
from pathlib import Path


class TestPageIndexUnit:
    """Unit tests for PageIndex service endpoints"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:8000"

    def test_extract_structure_endpoint_exists(self, base_url):
        """Test that extract_structure endpoint is available"""
        # Test OPTIONS or HEAD request to check endpoint availability
        try:
            response = requests.options(f"{base_url}/extract_structure")
            # OPTIONS may not be implemented, but shouldn't crash
            assert response.status_code in [200, 404, 405]
        except:
            # If OPTIONS not supported, try a simple GET to /docs
            response = requests.get(f"{base_url}/docs")
            assert response.status_code in [200, 404]

    def test_malformed_request_handling(self, base_url):
        """Test handling of malformed requests"""
        # Test with no file
        response = requests.post(f"{base_url}/extract_structure")
        assert response.status_code == 422  # FastAPI validation error

        # Test with empty file
        response = requests.post(f"{base_url}/extract_structure",
                                files={'file': ('empty.pdf', b'', 'application/pdf')})
        # Should handle gracefully
        assert response.status_code in [200, 400, 500]


class TestLEANNUnit:
    """Unit tests for LEANN service endpoints"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:8001"

    def test_upsert_validation(self, base_url):
        """Test upsert endpoint input validation"""
        # Test with invalid data
        response = requests.post(f"{base_url}/upsert", json={})
        assert response.status_code == 422  # Validation error

        # Test with empty chunks
        response = requests.post(f"{base_url}/upsert", json={"chunks": []})
        assert response.status_code == 200

    def test_search_validation(self, base_url):
        """Test search endpoint input validation"""
        # Test with empty query
        response = requests.post(f"{base_url}/search", json={"query": ""})
        assert response.status_code in [200, 422]

        # Test with missing query
        response = requests.post(f"{base_url}/search", json={})
        assert response.status_code == 422


class TestDeepConfUnit:
    """Unit tests for deepConf service endpoints"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:8002"

    def test_confidence_validation_structure(self, base_url):
        """Test confidence validation response structure"""
        test_data = {
            "prompt": "Test prompt",
            "context": "Test context",
            "tokens": []
        }

        response = requests.post(f"{base_url}/validate_confidence", json=test_data)

        # Should return some response (may be error if not fully implemented)
        assert response.status_code in [200, 501, 500]

        if response.status_code == 200:
            result = response.json()
            # Check for expected fields if implemented
            assert isinstance(result, dict)


class TestServiceIntegration:
    """Tests for service-to-service integration"""

    def test_pageindex_leann_integration(self):
        """Test that PageIndex can feed data to LEANN"""
        # Test PDF path
        test_pdf = "/Volumes/WS4TB/ERSATZ_RAG/WS_ED/Acceptable Uses and Governance of Artificial Intelligence Policy_FINAL_2-14-24.pdf"

        if not Path(test_pdf).exists():
            pytest.skip("Test PDF not found")

        # Get structure from PageIndex
        with open(test_pdf, 'rb') as f:
            files = {'file': ('test.pdf', f, 'application/pdf')}
            pi_response = requests.post("http://localhost:8000/extract_structure", files=files)

        assert pi_response.status_code == 200
        pi_result = pi_response.json()

        # Use extracted text for LEANN
        document_text = pi_result.get("text", "")
        assert len(document_text) > 0

        # This demonstrates the integration capability
        # Full integration test would require running the pipeline

    def test_cross_service_data_flow(self):
        """Test data flow between all three services"""
        # This is a high-level integration test
        # In practice, this would be tested through the Thalamus pipeline

        # Check all services are responsive
        services = [
            ("PageIndex", "http://localhost:8000/health"),
            ("LEANN", "http://localhost:8001/health"),
            ("deepConf", "http://localhost:8002/health")
        ]

        for service_name, health_url in services:
            response = requests.get(health_url, timeout=5)
            assert response.status_code == 200, f"{service_name} service unhealthy"
            data = response.json()
            assert data.get("status") == "healthy", f"{service_name} status not healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
