from fastapi.testclient import TestClient

from src.service import build_fallback_app


def test_meta_endpoint_reports_dataset():
    client = TestClient(build_fallback_app())
    response = client.get("/meta")
    payload = response.json()
    assert payload["dataset_id"] == "clinical_infections"
    assert payload["sections"] == "11"
    assert "warnings" in payload
    assert isinstance(payload["warnings"], list)


def test_sections_endpoint_lists_metadata():
    client = TestClient(build_fallback_app())
    response = client.get("/sections")
    payload = response.json()
    assert len(payload) >= 5
    diabetic_wound = next(item for item in payload if item["section_id"] == "infected_diabetic_wound_diabetic_wound_infection")
    assert "diabetic" in " ".join(diabetic_wound["aliases"]).lower()
    assert "vancomycin" in " ".join(diabetic_wound["entities"]).lower()


def test_query_endpoint_returns_section_text():
    """Test that the /query endpoint returns relevant section text."""
    app = build_fallback_app()
    client = TestClient(app)
    # Include required security headers
    headers = {
        "X-User-Region": "US",
        "X-PHI-Clearance": "true",
        "X-PII-Clearance": "true"
    }
    response = client.post("/query", json={"question": "What is the initial therapy for MRSA bacteremia?"}, headers=headers)
    payload = response.json()
    # With mock LLM, we get a mock answer
    assert "mock answer" in payload["answer"].lower() or "vancomycin" in payload["answer"].lower()
    assert len(payload["citations"]) > 0
    assert payload["confidence"] > 0


def test_query_uses_disambiguation_rules():
    client = TestClient(build_fallback_app())
    # Include required security headers
    headers = {
        "X-User-Region": "US",
        "X-PHI-Clearance": "true",
        "X-PII-Clearance": "true"
    }
    response = client.post("/query", json={"question": "Initial therapy for neutropenic fever?"}, headers=headers)
    payload = response.json()
    assert payload["section_id"] == "neutropenic_fever_neutropenic_fever"
    assert "neutropenic" in payload["answer"].lower()


def test_health_endpoint_reports_status():
    client = TestClient(build_fallback_app())
    response = client.get("/health")
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert "warnings" in payload
    assert "sections" in payload and payload["sections"] == 11
