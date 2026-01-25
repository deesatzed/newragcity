import json
from pathlib import Path

from src.ingestion_workflow import run_ingestion_with_metadata, run_ingestion_workflow
from src.pydantic_schemas import AJPack


def test_run_ingestion_workflow_builds_expected_pack(tmp_path):
    pack = run_ingestion_workflow("tests/fixtures/diabetes_handbook.pdf")
    assert isinstance(pack, AJPack)
    assert pack.manifest.dataset_id == "clinical_infections"
    assert pack.toc.toc_id == "infection_guidance_toc"
    section_ids = [section.section_id for entry in pack.content for section in entry.content]
    assert "infected_diabetic_wound_diabetic_wound_infection" in section_ids
    assert "urinary_tract_urinary_tract_infection" in section_ids
    assert len(section_ids) >= 10


def test_workflow_alignment_with_expected_fixture():
    fixtures_dir = Path(__file__).parent / "fixtures"
    reference = json.loads((fixtures_dir / "aj_pack_expected.json").read_text())

    pack = run_ingestion_workflow("tests/fixtures/diabetes_handbook.pdf")
    assert pack.manifest.dataset_id == reference["manifest"]["dataset_id"]
    assert pack.manifest.version == reference["manifest"]["version"]
    assert pack.toc.toc_id == reference["toc"]["toc_id"]
    observed_sections = {section.section_id for file in pack.content for section in file.content}
    for required in reference["required_sections"]:
        assert required in observed_sections


def test_run_ingestion_with_metadata_exposes_warnings():
    pack, warnings = run_ingestion_with_metadata("tests/fixtures/diabetes_handbook.pdf")
    assert isinstance(pack, AJPack)
    assert isinstance(warnings, list)
