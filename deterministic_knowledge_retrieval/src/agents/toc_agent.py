"""
TOC Agent: Router and Oracle

Reference: agnoMCPnanobot.txt lines 431-441

The TOC Agent is responsible for intelligent routing of queries to the most
relevant sections in the AJ Pack. It uses the Table of Contents (TOC) metadata
to make deterministic, explainable routing decisions.

Key Responsibilities:
1. Normalize and tokenize queries
2. Apply disambiguation rules from the TOC
3. Score candidate sections based on aliases, entities, and text matches
4. Recommend the best sections for context loading
"""

import re
from typing import List, Tuple, Dict, Sequence, Iterable, Any
from ..pydantic_schemas import TOC


class TOCAgent:
    """
    The TOC Agent acts as the router and oracle for the Doc-MCP system.
    
    Reference: agnoMCPnanobot.txt lines 431-441
    
    This agent:
    - Reads the TOC to understand document structure
    - Uses aliases, entities, and disambiguation rules for routing
    - Provides deterministic, explainable section recommendations
    
    This is a "simulation" agent - it implements the agent pattern without
    requiring the full Agno framework. In production, this would be replaced
    with an actual Agno Agent that uses KnowledgeTools.
    """
    
    def __init__(self, toc: TOC, sections: List[Dict[str, Any]]):
        """
        Initialize the TOC Agent.
        
        Args:
            toc: The Table of Contents from the AJ Pack
            sections: List of section metadata dictionaries
        """
        self.toc = toc
        self.sections = sections
    
    def route_query(self, query: str) -> List[Tuple[str, str, float, Dict[str, Any]]]:
        """
        Route a query to the most relevant sections.
        
        Reference: AJrag.txt §3.1 - TOC Agent routing logic
        
        This is the main entry point for the TOC Agent. It:
        1. Normalizes the query
        2. Applies disambiguation rules
        3. Scores all sections
        4. Returns ranked recommendations
        
        Args:
            query: The user's question
        
        Returns:
            List of (file_id, section_id, score, section_metadata) tuples,
            ranked by relevance (highest first)
        """
        # Step 1: Normalize query
        tokens = self._normalize(query)
        
        # Step 2: Apply disambiguation rules
        disambiguation_preferences = self._apply_disambiguation(tokens)
        preferred_pairs = set(disambiguation_preferences)
        
        # Step 3: Score all sections
        ranked = []
        for section in self.sections:
            score = self._score_section(tokens, section, preferred_pairs)
            ranked.append((
                section['file_id'],
                section['section_id'],
                score,
                section
            ))
        
        # Step 4: Sort by score (highest first)
        ranked.sort(key=lambda item: item[2], reverse=True)
        
        return ranked
    
    def get_top_section(self, query: str) -> Tuple[float, Dict[str, Any]]:
        """
        Get the single best section for a query.
        
        This is a convenience method that returns just the top-ranked section.
        
        Args:
            query: The user's question
        
        Returns:
            Tuple of (score, section_metadata)
        """
        ranked = self.route_query(query)
        if not ranked:
            return (0.0, {})
        
        _, _, score, section = ranked[0]
        return (score, section)
    
    def _normalize(self, text: str) -> Sequence[str]:
        """
        Normalize text into tokens.
        
        Reference: Implements the preprocessing step described in
        agnoMCPnanobot.txt for the TOC Agent.
        
        This extracts lowercase alphanumeric tokens, which provides:
        - Case-insensitive matching
        - Removal of punctuation
        - Consistent tokenization
        
        Args:
            text: Raw text to normalize
        
        Returns:
            Sequence of normalized tokens
        """
        return re.findall(r'[a-z0-9]+', text.lower())
    
    def _apply_disambiguation(self, tokens: Sequence[str]) -> List[Tuple[str, str]]:
        """
        Apply TOC disambiguation rules.
        
        Reference: AJrag.txt §5.2 - Disambiguation rules
        
        Disambiguation rules boost specific sections when certain trigger
        words appear together in a query. For example, if "DKA" and
        "electrolytes" both appear, prefer sections about diabetic ketoacidosis.
        
        Args:
            tokens: Normalized query tokens
        
        Returns:
            List of (file_id, section_id) tuples that should be boosted
        """
        hits: List[Tuple[str, str]] = []
        token_set = set(tokens)
        
        for rule in self.toc.disambiguation:
            # Check if ALL triggers in the rule are present
            if all(trigger.lower() in token_set for trigger in rule.if_all):
                # If yes, add all preferred sections to the boost list
                hits.extend((file_id, section_id) for file_id, section_id in rule.prefer)
        
        return hits
    
    def _score_section(
        self,
        tokens: Sequence[str],
        section: Dict[str, Any],
        preferred_pairs: set
    ) -> float:
        """
        Score a section's relevance to the query.
        
        Reference: AJrag.txt §3.1 - TOC Agent candidate ranking
        
        The scoring algorithm uses weighted components:
        - Text hits (weight: 2) - Direct keyword matches in section text
        - Alias hits (weight: 3) - Matches to section aliases
        - Entity hits (weight: 1) - Matches to tagged entities
        - Disambiguation boost (+100) - If section is in preferred list
        
        Args:
            tokens: Normalized query tokens
            section: Section metadata dictionary
            preferred_pairs: Set of (file_id, section_id) tuples to boost
        
        Returns:
            Relevance score (higher is better)
        """
        # Base score from text matches
        base = self._text_hits(tokens, section.get('text', ''))
        
        # Bonus from alias matches
        alias_bonus = self._alias_hits(tokens, section.get('aliases', []))
        
        # Bonus from entity matches
        entity_bonus = self._entity_hits(tokens, section.get('entities', []))
        
        # Calculate weighted total
        total = base * 2 + alias_bonus * 3 + entity_bonus
        
        # Apply disambiguation boost
        if preferred_pairs and (section['file_id'], section['section_id']) in preferred_pairs:
            total += 100
        
        return float(total)
    
    def _alias_hits(self, tokens: Sequence[str], aliases: Iterable[str]) -> int:
        """
        Count how many query tokens match section aliases.
        
        Reference: AJrag.txt §2.2 Step 4 - Aliases improve routing
        
        Args:
            tokens: Normalized query tokens
            aliases: List of alias strings for the section
        
        Returns:
            Number of matching tokens
        """
        alias_tokens = {
            token
            for alias in aliases
            for token in self._normalize(str(alias))
        }
        return sum(1 for token in tokens if token in alias_tokens)
    
    def _entity_hits(self, tokens: Sequence[str], entities: Iterable[str]) -> int:
        """
        Count how many query tokens match section entities.
        
        Reference: AJrag.txt §2.2 Step 1 - Entity extraction and tagging
        
        Args:
            tokens: Normalized query tokens
            entities: List of entity strings for the section
        
        Returns:
            Number of matching tokens
        """
        entity_tokens = {
            token
            for entity in entities
            for token in self._normalize(str(entity))
        }
        return sum(1 for token in tokens if token in entity_tokens)
    
    def _text_hits(self, tokens: Sequence[str], text: str) -> int:
        """
        Count how many query tokens appear in section text.
        
        This is the baseline keyword matching component.
        
        Args:
            tokens: Normalized query tokens
            text: Section text content
        
        Returns:
            Number of matching tokens
        """
        section_tokens = self._normalize(text)
        return sum(1 for token in tokens if token in section_tokens)
    
    def get_routing_trace(self, query: str, top_n: int = 3) -> str:
        """
        Get a human-readable trace of the routing decision.
        
        This is useful for debugging and explainability.
        
        Args:
            query: The user's question
            top_n: Number of top sections to include in trace
        
        Returns:
            String describing the routing decision
        """
        tokens = self._normalize(query)
        ranked = self.route_query(query)
        
        trace_lines = [
            f"TOC Agent Routing Trace",
            f"Query: {query}",
            f"Tokens: {', '.join(tokens)}",
            f"",
            f"Top {top_n} Sections:"
        ]
        
        for i, (file_id, section_id, score, section) in enumerate(ranked[:top_n], 1):
            trace_lines.append(
                f"{i}. [{file_id}/{section_id}] {section.get('label', 'Unknown')} "
                f"(score: {score:.1f})"
            )
        
        return "\n".join(trace_lines)
