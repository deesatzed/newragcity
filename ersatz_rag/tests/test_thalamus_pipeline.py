import os
import requests
import pytest

THALAMUS_URL = os.getenv("THALAMUS_URL", "http://localhost:8003").rstrip("/")


def thalamus_available() -> bool:
    try:
        r = requests.get(f"{THALAMUS_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


@pytest.mark.skipif(not thalamus_available(), reason="thalamus not running")
class TestThalamusPipeline:
    def test_process_pipeline_structure(self):
        payload = {
            "question": "acceptable use policy",
            "confidence_threshold": 0.7,
            "limit": 3,
        }
        r = requests.post(f"{THALAMUS_URL}/process_pipeline", json=payload, timeout=10)
        assert r.status_code == 200
        data = r.json()
        # Structural assertions (tolerant to empty results)
        assert isinstance(data, dict)
        for key in ["processed", "status", "answer", "confidence", "citations", "results"]:
            assert key in data
        assert isinstance(data["citations"], list)
        assert isinstance(data["results"], list)
        assert data["status"] == "success"
