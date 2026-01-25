"""
Data contracts for the Agno/Nanobot pipeline.

These mirror the structures defined in the repository design docs and provide
typed access to AJ Pack content and related metadata.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AJPackManifest(BaseModel):
    dataset_id: str
    version: str
    files: List[Dict[str, str]]
    built_at: str


class SectionTOC(BaseModel):
    section_id: str
    label: str
    pointer: str
    token_estimate: int
    aliases: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)


class FileTOC(BaseModel):
    file_id: str
    sections: List[SectionTOC]


class DisambiguationRule(BaseModel):
    if_all: List[str]
    prefer: List[List[str]]


class SecurityMetadata(BaseModel):
    residency: Optional[str] = None
    pii: bool = False
    phi: bool = False


class TOC(BaseModel):
    toc_id: str
    index: List[FileTOC]
    disambiguation: List[DisambiguationRule] = Field(default_factory=list)
    security: SecurityMetadata


class AJSectionNode(BaseModel):
    section_id: str
    label: str
    summary: str
    text_or_data: str
    entities: List[str] = Field(default_factory=list)
    parents: List[str] = Field(default_factory=list)
    children: List[str] = Field(default_factory=list)
    cross_refs: List[str] = Field(default_factory=list)


class AJContent(BaseModel):
    file_id: str
    content: List[AJSectionNode]


class AJPack(BaseModel):
    manifest: AJPackManifest
    toc: TOC
    content: List[AJContent]


class AtlasAskResponse(BaseModel):
    answer: str = Field(description="Final, synthesized answer to a user query.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0 and 1.")
    citations: List[str] = Field(description="Section IDs that support the answer.")
    trace: str = Field(description="Brief trace of agents/tools used during answer generation.")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[str]
    confidence: float
    section_id: str
    label: str

class SectionSummary(BaseModel):
    section_id: str
    label: str
    file_id: str
    aliases: List[str]
    entities: List[str]
