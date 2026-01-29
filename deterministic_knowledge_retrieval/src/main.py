"""
Application entrypoint mirroring the architecture described in agnoMCPnanobot.txt.

The heavy dependencies (Agno, LanceDB, OpenAI, FastAPI) are imported lazily so
that the module remains importable in environments that have not yet installed
them. `setup_app()` should only be called once all required packages are
available.
"""

from __future__ import annotations

from typing import Any, Optional

from .doc_mcp_team import MissingAgnoDependency, get_doc_mcp_team
from .ingestion_workflow import run_ingestion_workflow
from .service import build_fallback_app


def setup_app() -> Any:
    """Instantiate the AgentOS application that serves the Doc-MCP team."""

    try:
        from dotenv import load_dotenv
        from agno.os import AgentOS
        from agno.knowledge.knowledge import Knowledge
        from agno.vectordb.lancedb import LanceDb, SearchType
        from agno.knowledge.embedder.openai import OpenAIEmbedder
    except ImportError as exc:  # pragma: no cover
        raise MissingAgnoDependency(
            "Full AgentOS setup requires agno, lancedb, python-dotenv, and related "
            "packages. Install dependencies from requirements.txt or "
            "use the fallback FastAPI service."
        ) from exc

    load_dotenv()

    # Run ingestion workflow to build AJ Pack from JSON files in project root
    aj_pack = run_ingestion_workflow()

    db_uri = f"/tmp/lancedb/{aj_pack.manifest.dataset_id}"
    knowledge_base = Knowledge(
        vector_db=LanceDb(
            uri=db_uri,
            table_name="source_content",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        )
    )
    # knowledge_base.clear_content()  # API changed in newer agno - table auto-created fresh
    for file_content in aj_pack.content:
        for section in file_content.content:
            knowledge_base.add_content(
                name=section.label,
                text_content=section.text_or_data,
                metadata={
                    "file_id": file_content.file_id,
                    "section_id": section.section_id,
                },
            )

    team = get_doc_mcp_team(knowledge_base)
    agent_os = AgentOS(
        id=f"doc-mcp-server-{aj_pack.manifest.dataset_id}",
        teams=[team],
        description=f"Query server for {aj_pack.manifest.dataset_id}",
    )
    return agent_os.get_app()


def get_app_or_none() -> Optional[Any]:
    """
    Provide an import-friendly way to retrieve the AgentOS application.

    When optional dependencies are missing, `None` is returned so callers can
    handle the condition gracefully (e.g., during tests).
    """

    try:
        return setup_app()
    except MissingAgnoDependency:
        return build_fallback_app()


agent_os_app = get_app_or_none()


if __name__ == "__main__":
    if agent_os_app is None:
        agent_os_app = build_fallback_app()
    print("Application initialised. Run `uvicorn src.main:agent_os_app --reload` to serve.")
