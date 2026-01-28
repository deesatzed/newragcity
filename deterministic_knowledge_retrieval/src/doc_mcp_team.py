"""
Factory for the Doc-MCP server team.

The real implementation depends on the Agno framework. To keep the repository
importable without optional dependencies, imports are deferred until the
function is invoked.
"""

from typing import Any

from .pydantic_schemas import AtlasAskResponse


class MissingAgnoDependency(RuntimeError):
    """Raised when the Agno framework is unavailable at runtime."""


def get_doc_mcp_team(knowledge_base: Any):
    """
    Build the Doc-MCP server team using Agno primitives.

    Parameters
    ----------
    knowledge_base:
        Agno Knowledge instance configured with document embeddings.
    """

    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.team import Team
        from agno.tools.knowledge import KnowledgeTools
    except ImportError as exc:  # pragma: no cover - exercised when dependency missing
        raise MissingAgnoDependency(
            "Agno is required to build the Doc-MCP team. "
            "Install dependencies from requirements.txt."
        ) from exc

    toc_agent = Agent(
        name="TOC_Agent",
        role="Router and Oracle",
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=[KnowledgeTools(knowledge=knowledge_base)],
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=[
            "You are the Table of Contents agent responsible for routing.",
            "Use the knowledge search tool to retrieve the best candidate sections.",
            "Return the selected sections to the team lead for answer synthesis.",
        ],
    )

    answer_verifier_agent = Agent(
        name="Answer_Verifier_Agent",
        role="Answer Synthesizer and Verifier",
        model=OpenAIChat(id="gpt-4o-mini"),
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=[
            "Synthesize a comprehensive answer grounded in the provided sections.",
            "Verify that each statement is supported by the source content.",
            "Return citations referencing section IDs from the AJ Pack.",
        ],
    )

    team = Team(
        name="Doc_MCP_Server_Team",
        model=OpenAIChat(id="gpt-4o"),
        members=[toc_agent, answer_verifier_agent],
        instructions=[
            "Lead the Doc-MCP server workflow.",
            "Delegate routing to TOC_Agent and synthesis to Answer_Verifier_Agent.",
            "Emit results that comply with the AtlasAskResponse schema.",
        ],
        output_schema=AtlasAskResponse,
        share_member_interactions=True,
    )

    return team
