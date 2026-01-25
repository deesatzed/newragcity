"""
Utilities for transforming infection JSON documents into AJ Pack sections.

Each JSON file in the repository root follows a common schema containing
`documentInfo` and an array of `infections`. We parse those files, extract the
important clinical guidance, and create richly annotated section payloads that
feed the ingestion workflow.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from json import JSONDecodeError


@dataclass
class InfectionSection:
    file_id: str
    section_id: str
    label: str
    summary: str
    text: str
    aliases: List[str]
    entities: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    token_estimate: int = 0


@dataclass
class DocumentSections:
    file_id: str
    title: str
    sections: List[InfectionSection]


def slugify(value: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", value.lower())
    return "_".join(tokens) if tokens else "section"


def load_infection_documents(base_path: Path | None = None) -> Tuple[List[DocumentSections], List[str]]:
    base_dir = base_path or Path(__file__).resolve().parents[1]
    documents: List[DocumentSections] = []
    warnings: List[str] = []

    for json_path in sorted(base_dir.glob("*.json")):
        try:
            data = json.loads(json_path.read_text())
        except JSONDecodeError as exc:
            warnings.append(f"{json_path.name}: failed to parse JSON ({exc})")
            continue

        try:
            _validate_document(data, json_path)
        except ValueError as exc:
            warnings.append(str(exc))
            continue

        infections = data.get("infections", [])
        if not infections:
            warnings.append(f"{json_path.name}: no infections defined; skipping.")
            continue

        file_id = slugify(json_path.stem)
        title = data.get("documentInfo", {}).get("title", json_path.stem)
        sections: List[InfectionSection] = []
        for infection in infections:
            section = _build_section(file_id, infection)
            if section is not None:
                sections.append(section)
        if sections:
            documents.append(DocumentSections(file_id=file_id, title=title, sections=sections))
        else:
            warnings.append(f"{json_path.name}: infections present but no usable pathways extracted.")
    return documents, warnings


def _validate_document(data: dict, source_path: Path) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{source_path.name}: root JSON payload must be an object.")

    infections = data.get("infections")
    if infections is None:
        raise ValueError(f"{source_path.name}: missing 'infections' array.")
    if not isinstance(infections, list):
        raise ValueError(f"{source_path.name}: 'infections' must be a list.")

    for index, infection in enumerate(infections):
        if not isinstance(infection, dict):
            raise ValueError(f"{source_path.name}: infection entry #{index} is not an object.")
        if not infection.get("id") and not infection.get("name"):
            raise ValueError(f"{source_path.name}: infection entry #{index} missing 'id' or 'name'.")
        pathways = infection.get("pathways")
        if pathways is None:
            continue
        if not isinstance(pathways, list):
            raise ValueError(f"{source_path.name}: infection '{infection.get('id')}' pathways must be a list.")
        for p_index, pathway in enumerate(pathways):
            if not isinstance(pathway, dict):
                raise ValueError(
                    f"{source_path.name}: infection '{infection.get('id')}' pathway #{p_index} is not an object."
                )


def _build_section(file_id: str, infection: dict) -> InfectionSection | None:
    infection_id = infection.get("id") or infection.get("name")
    name = infection.get("name") or infection_id
    if not infection_id or not name:
        return None

    section_slug = slugify(f"{infection_id}")
    section_id = f"{file_id}_{section_slug}"

    diagnostics = infection.get("diagnostics") or {}
    notes = diagnostics.get("notes") or []
    pathways = infection.get("pathways") or []

    sections: List[str] = []
    if notes:
        sections.append("Diagnostics: " + " ".join(notes))

    entities: List[str] = [name]
    keywords = _keywords_from_label(name)
    aliases = set(_generate_alias_variants(name))
    aliases.add(section_slug.replace("_", " "))

    for pathway in pathways:
        if not isinstance(pathway, dict):
            continue
        sections.append(_pathway_summary(pathway))
        entities.extend(_collect_drug_names(pathway))
        label = pathway.get("label")
        if isinstance(label, str) and label:
            aliases.update(_generate_alias_variants(label))
            keywords.extend(_keywords_from_label(label))

    text = "\n\n".join(section.strip() for section in sections if section.strip())
    summary = _make_summary(text) or f"Guidance for {name}."
    token_estimate = max(60, len(text.split()))

    return InfectionSection(
        file_id=file_id,
        section_id=section_id,
        label=name,
        summary=summary,
        text=text,
        aliases=sorted(set(alias for alias in aliases if alias)),
        entities=sorted(set(entities)),
        keywords=sorted(set(keywords)),
        token_estimate=token_estimate,
    )


def _keywords_from_label(label: str) -> List[str]:
    return [token for token in re.findall(r"[a-z0-9]+", label.lower()) if len(token) >= 4]


def _collect_drug_names(pathway: dict) -> List[str]:
    names: List[str] = []
    for recommendation in pathway.get("treatmentRecommendations", []) or []:
        if not isinstance(recommendation, dict):
            continue
        for regimen in recommendation.get("regimens", []) or []:
            if not isinstance(regimen, dict):
                continue
            for drug in regimen.get("primaryDrugs", []) or []:
                if not isinstance(drug, dict):
                    continue
                drug_name = drug.get("name")
                if drug_name:
                    names.append(drug_name)
    return names


def _pathway_summary(pathway: dict) -> str:
    label = pathway.get("label", "Treatment Pathway")
    lines = [f"Pathway: {label}"]

    eligibility = pathway.get("eligibilityCriteria") or {}
    criteria_fragments = []
    for key, values in eligibility.items():
        if isinstance(values, list):
            joined = ", ".join(values)
        else:
            joined = str(values)
        criteria_fragments.append(f"{key.replace('_', ' ')}: {joined}")
    if criteria_fragments:
        lines.append("Eligibility: " + "; ".join(criteria_fragments))

    duration = (pathway.get("duration") or {}).get("notes")
    if duration:
        lines.append("Duration: " + " ".join(duration))

    consults = pathway.get("consults") or []
    if consults:
        lines.append("Consults: " + "; ".join(consults))

    treatment_lines: List[str] = []
    for recommendation in pathway.get("treatmentRecommendations", []) or []:
        if not isinstance(recommendation, dict):
            continue
        allergy_profile = ", ".join(recommendation.get("allergyProfile", []) or [])
        regimens = recommendation.get("regimens", []) or []
        regimen_descriptions = []
        for regimen in regimens:
            if not isinstance(regimen, dict):
                continue
            drugs = ", ".join(
                drug.get("name", "")
                for drug in (regimen.get("primaryDrugs", []) or [])
                if isinstance(drug, dict)
            )
            notes: Sequence[str] = regimen.get("notes", []) or []
            note_text = " ".join(notes)
            regimen_descriptions.append(f"{drugs} ({note_text})".strip())
        if regimen_descriptions:
            prefix = f"Allergy profile [{allergy_profile}]" if allergy_profile else "Regimens"
            treatment_lines.append(prefix + ": " + "; ".join(filter(None, regimen_descriptions)))
    if treatment_lines:
        lines.extend(treatment_lines)

    return " ".join(line for line in lines if line)


def _make_summary(text: str, max_words: int = 30) -> str:
    words = text.split()
    if not words:
        return ""
    snippet = " ".join(words[:max_words])
    return snippet + ("…" if len(words) > max_words else "")


def _generate_alias_variants(value: str) -> List[str]:
    if not value:
        return []
    variants = {value.strip()}
    variants.add(value.lower())
    variants.add(value.replace("-", " "))
    variants.add(value.replace(" ", "-"))

    no_parentheses = re.sub(r"\s*\(.*?\)", "", value).strip()
    if no_parentheses:
        variants.add(no_parentheses)
        variants.add(no_parentheses.lower())

    parts = re.split(r"[\/,]", no_parentheses or value)
    for part in parts:
        cleaned = part.strip()
        if cleaned:
            variants.add(cleaned)
            variants.add(cleaned.lower())
            variants.add(cleaned.replace("-", " "))

    slug = slugify(value).replace("_", " ")
    if slug:
        variants.add(slug)

    return sorted({alias for alias in variants if alias})
