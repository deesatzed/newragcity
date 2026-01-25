"""
Lightweight ingestion workflow that mirrors the five-step pipeline described in
AJrag.txt. It produces a deterministic AJ Pack that can be used as a fixture or
starting point for more advanced automation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List

from .data_loader import DocumentSections, load_infection_documents
from .pydantic_schemas import (
    AJContent,
    AJPack,
    AJPackManifest,
    AJSectionNode,
    FileTOC,
    SectionTOC,
    SecurityMetadata,
    TOC,
    DisambiguationRule,
)


WorkflowStep = Callable[[Dict[str, object]], Dict[str, object]]


def source_profiler(state: Dict[str, object]) -> Dict[str, object]:
    documents, warnings = load_infection_documents()
    state["documents"] = documents
    state["warnings"] = warnings
    state["profile"] = {
        "structure": "json_documents",
        "sources": [document.file_id for document in documents],
        "detected_sections": sum(len(document.sections) for document in documents),
        "warnings": warnings,
    }
    return state


def schema_selector(state: Dict[str, object]) -> Dict[str, object]:
    state["schema"] = "chapter_per_file"
    return state


def aj_json_builder(state: Dict[str, object]) -> Dict[str, object]:
    documents: List[DocumentSections] = state.get("documents", [])  # type: ignore[assignment]
    contents: List[AJContent] = []
    sections_meta: List[Dict[str, object]] = []

    for document in documents:
        section_nodes: List[AJSectionNode] = []
        for index, section in enumerate(document.sections):
            pointer = f"/sections/{index}"
            section_nodes.append(
                AJSectionNode(
                    section_id=section.section_id,
                    label=section.label,
                    summary=section.summary,
                    text_or_data=section.text,
                    entities=section.entities,
                )
            )
            sections_meta.append(
                {
                    "file_id": document.file_id,
                    "section_id": section.section_id,
                    "label": section.label,
                    "aliases": section.aliases,
                    "entities": section.entities,
                    "pointer": pointer,
                    "token_estimate": section.token_estimate,
                    "keywords": section.keywords,
                }
            )

        if section_nodes:
            contents.append(AJContent(file_id=document.file_id, content=section_nodes))

    state["content"] = contents
    state["sections_meta"] = sections_meta
    return state


def toc_synthesizer(state: Dict[str, object]) -> Dict[str, object]:
    sections_meta: List[Dict[str, object]] = state.get("sections_meta", [])  # type: ignore[assignment]

    file_sections: Dict[str, List[SectionTOC]] = {}
    for meta in sections_meta:
        file_id = meta["file_id"]
        file_sections.setdefault(file_id, []).append(
            SectionTOC(
                section_id=meta["section_id"],
                label=meta["label"],
                pointer=meta["pointer"],
                token_estimate=int(meta["token_estimate"]),
                aliases=list(meta["aliases"]),
                entities=list(meta["entities"]),
            )
        )

    index = [
        FileTOC(file_id=file_id, sections=sections)
        for file_id, sections in sorted(file_sections.items())
    ]

    disambiguation_rules: List[DisambiguationRule] = []
    for meta in sections_meta:
        keywords: List[str] = list(meta.get("keywords", []))
        if len(keywords) >= 2:
            disambiguation_rules.append(
                DisambiguationRule(if_all=keywords[:2], prefer=[[meta["file_id"], meta["section_id"]]])
            )

    state["toc"] = TOC(
        toc_id="infection_guidance_toc",
        index=index,
        disambiguation=disambiguation_rules,
        security=SecurityMetadata(residency="US", phi=True),
    )
    return state


def assemble_and_audit_pack(state: Dict[str, object]) -> Dict[str, object]:
    contents: List[AJContent] = state["content"]  # type: ignore[assignment]
    toc: TOC = state["toc"]  # type: ignore[assignment]
    state["aj_pack"] = AJPack(
        manifest=AJPackManifest(
            dataset_id="clinical_infections",
            version="1.1.0",
            files=[
                {"file_id": entry.file_id, "path": f"json/{entry.file_id}.json"}
                for entry in contents
            ],
            built_at=datetime.now(timezone.utc).isoformat(),
        ),
        toc=toc,
        content=contents,
    )
    return state


@dataclass
class IngestionWorkflow:
    """Minimal orchestrator for the deterministic ingestion pipeline."""

    steps: List[WorkflowStep]
    last_warnings: List[str] = field(default_factory=list)

    def run(self, input_payload: str) -> AJPack:
        state: Dict[str, object] = {"input": input_payload}
        for step in self.steps:
            state = step(state)
        assemble_and_audit_pack(state)
        self.last_warnings = list(state.get("warnings", []))  # type: ignore[arg-type]
        return state["aj_pack"]  # type: ignore[return-value]


workflow = IngestionWorkflow(
    steps=[
        source_profiler,
        schema_selector,
        aj_json_builder,
        toc_synthesizer,
    ],
)


def run_ingestion_with_metadata(source: str = "") -> tuple[AJPack, List[str]]:
    """
    Run the ingestion workflow and return both the AJ Pack and any loader warnings.
    
    Args:
        source: Optional source identifier (currently unused - auto-discovers JSON files)
    
    Returns:
        Tuple of (AJPack, warnings list)
    """
    pack = workflow.run(source)
    warnings = list(getattr(workflow, "last_warnings", []))
    return pack, warnings


def run_ingestion_workflow(source: str = "") -> AJPack:
    """
    Public helper that mirrors the behaviour expected by the design docs.
    
    Auto-discovers and ingests all JSON files in the project root that match
    the infection disease format.

    Parameters
    ----------
    source:
        Optional source identifier (currently unused - auto-discovers JSON files)
    
    Returns
    -------
    AJPack:
        Complete Universal Knowledge Pack with manifest, TOC, and sections
    """
    pack, _ = run_ingestion_with_metadata(source)
    return pack
