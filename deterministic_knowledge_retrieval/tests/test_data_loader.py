import json
from pathlib import Path

from src.data_loader import load_infection_documents


def test_load_infection_documents_enriches_aliases_and_entities(tmp_path):
    sample = {
        "documentInfo": {"title": "Demo Guide"},
        "infections": [
            {
                "id": "demo_infection",
                "name": "Demo Infection (Adult)",
                "diagnostics": {"notes": ["Example diagnostic note."]},
                "pathways": [
                    {
                        "label": "Severe Presentation",
                        "eligibilityCriteria": {"clinicalState": ["severe"]},
                        "treatmentRecommendations": [
                            {
                                "allergyProfile": ["none"],
                                "regimens": [
                                    {
                                        "primaryDrugs": [{"name": "ceftriaxone"}],
                                        "notes": ["Administer intravenously."],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }
    (tmp_path / "demo.json").write_text(json.dumps(sample))

    documents, warnings = load_infection_documents(tmp_path)
    assert warnings == []
    assert len(documents) == 1

    section = documents[0].sections[0]
    aliases_lower = {alias.lower() for alias in section.aliases}
    assert "demo infection" in aliases_lower
    assert "severe presentation" in aliases_lower
    entities_lower = {entity.lower() for entity in section.entities}
    assert "ceftriaxone" in entities_lower


def test_invalid_documents_emit_warnings(tmp_path):
    good_payload = {
        "documentInfo": {"title": "Valid"},
        "infections": [
            {"id": "valid", "name": "Valid", "pathways": [{"label": "Default"}]},
        ],
    }
    bad_payload = {"infections": ["invalid"]}

    (tmp_path / "good.json").write_text(json.dumps(good_payload))
    (tmp_path / "bad.json").write_text(json.dumps(bad_payload))

    documents, warnings = load_infection_documents(tmp_path)

    assert len(documents) == 1
    assert any("bad.json" in warning for warning in warnings)
