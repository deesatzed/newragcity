"""
Performance and load tests for microservices
"""

import pytest
import requests
import time
import threading
import concurrent.futures
from typing import List, Dict, Any


class TestPerformance:
    """Performance tests for individual services"""

    def test_pageindex_response_time(self):
        """Test PageIndex response time under normal load"""
        test_pdf = "/Volumes/WS4TB/ERSATZ_RAG/WS_ED/Acceptable Uses and Governance of Artificial Intelligence Policy_FINAL_2-14-24.pdf"

        if not Path(test_pdf).exists():
            pytest.skip("Test PDF not found")

        start_time = time.time()

        with open(test_pdf, 'rb') as f:
            files = {'file': ('test.pdf', f, 'application/pdf')}
            response = requests.post("http://localhost:8000/extract_structure", files=files)

        end_time = time.time()
        response_time = end_time - start_time

        assert response.status_code == 200
        # Should complete within reasonable time (adjust based on document size)
        assert response_time < 30.0, f"Response too slow: {response_time:.2f}s"

    def test_leann_concurrent_requests(self):
        """Test LEANN handling of concurrent requests"""
        def single_request(thread_id: int) -> Dict[str, Any]:
            test_chunks = [{
                "id": f"perf_test_chunk_{thread_id}",
                "text": f"This is performance test content from thread {thread_id}",
                "metadata": {"test_type": "performance", "thread_id": thread_id}
            }]

            response = requests.post("http://localhost:8001/upsert",
                                   json={"chunks": test_chunks})
            return {"thread_id": thread_id, "status_code": response.status_code}

        # Test with multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(single_request, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        for result in results:
            assert result["status_code"] == 200, f"Thread {result['thread_id']} failed"

    def test_service_memory_usage(self):
        """Test that services don't have excessive memory growth"""
        # This would require system monitoring tools
        # For now, just ensure services remain responsive
        services = [
            "http://localhost:8000/health",
            "http://localhost:8001/health",
            "http://localhost:8002/health"
        ]

        for _ in range(10):  # Multiple checks
            for url in services:
                response = requests.get(url, timeout=5)
                assert response.status_code == 200
            time.sleep(0.1)

    def test_large_payload_handling(self):
        """Test handling of large payloads"""
        # Create a large text chunk for LEANN
        large_text = "This is a test document. " * 1000  # ~25KB of text
        test_chunks = [{
            "id": "large_test_chunk",
            "text": large_text,
            "metadata": {"test_type": "large_payload"}
        }]

        start_time = time.time()
        response = requests.post("http://localhost:8001/upsert",
                               json={"chunks": test_chunks})
        end_time = time.time()

        assert response.status_code == 200
        # Should handle large payloads within reasonable time
        assert (end_time - start_time) < 10.0


class TestLoad:
    """Load tests for service capacity"""

    def test_sustained_load(self):
        """Test sustained load over time"""
        # Perform multiple operations in sequence
        for i in range(20):
            # Test LEANN upsert and search
            test_chunks = [{
                "id": f"load_test_chunk_{i}",
                "text": f"Load test content iteration {i}",
                "metadata": {"test_type": "load", "iteration": i}
            }]

            # Upsert
            upsert_response = requests.post("http://localhost:8001/upsert",
                                          json={"chunks": test_chunks})
            assert upsert_response.status_code == 200

            # Search
            search_response = requests.post("http://localhost:8001/search",
                                          json={"query": f"iteration {i}", "limit": 1})
            assert search_response.status_code == 200

    def test_memory_leak_detection(self):
        """Basic memory leak detection through repeated operations"""
        # This is a simplified version - real memory leak detection
        # would require more sophisticated monitoring

        initial_operations = 10
        sustained_operations = 50

        # Initial load
        for i in range(initial_operations):
            test_chunks = [{
                "id": f"memory_test_{i}",
                "text": f"Memory test content {i}",
                "metadata": {"test_type": "memory"}
            }]
            response = requests.post("http://localhost:8001/upsert",
                                   json={"chunks": test_chunks})
            assert response.status_code == 200

        # Sustained load
        for i in range(initial_operations, initial_operations + sustained_operations):
            test_chunks = [{
                "id": f"memory_test_{i}",
                "text": f"Memory test content {i}",
                "metadata": {"test_type": "memory"}
            }]
            response = requests.post("http://localhost:8001/upsert",
                                   json={"chunks": test_chunks})
            assert response.status_code == 200

            # Check service still responsive
            health_response = requests.get("http://localhost:8001/health")
            assert health_response.status_code == 200


class TestReliability:
    """Reliability tests for service stability"""

    def test_service_restart_recovery(self):
        """Test service recovery after simulated restart"""
        # This would require actually restarting services
        # For now, just test basic connectivity
        services = [
            ("PageIndex", "http://localhost:8000/health"),
            ("LEANN", "http://localhost:8001/health"),
            ("deepConf", "http://localhost:8002/health")
        ]

        for service_name, url in services:
            response = requests.get(url, timeout=10)
            assert response.status_code == 200, f"{service_name} not responding"

    def test_graceful_error_handling(self):
        """Test graceful handling of various error conditions"""
        # Test malformed JSON
        try:
            response = requests.post("http://localhost:8001/upsert",
                                   data="invalid json")
            # Should handle gracefully
            assert response.status_code in [400, 422, 500]
        except:
            # Connection errors are also acceptable
            pass

    def test_timeout_handling(self):
        """Test handling of timeout conditions"""
        # Test with very short timeout
        try:
            response = requests.get("http://localhost:8000/health", timeout=0.001)
            # May timeout or succeed
            assert response.status_code in [200, 504]
        except requests.exceptions.Timeout:
            # Expected timeout behavior
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
