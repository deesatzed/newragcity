"""
Loader Agent: Context Manager with Token Budget Enforcement

Reference: AJrag.txt §3.1 - Loader-1 / Loader-2

The Loader Agent is responsible for managing context under strict token budgets.
It simulates the REQUEST_LOAD / RELEASE verbs described in the design documents.

Key Responsibilities:
1. Track token usage against a budget
2. Load sections into context
3. Release sections when budget is exceeded
4. Prevent context thrash
5. Provide context assembly for the LLM
"""

from typing import Dict, List, Tuple, Optional


class LoaderAgent:
    """
    The Loader Agent manages context loading under strict token budgets.
    
    Reference: AJrag.txt §3.1 - Loader-1 / Loader-2 agents
    
    This agent:
    - Enforces token budgets (default: 4000 tokens)
    - Tracks which sections are loaded
    - Prevents context thrash by monitoring load/release patterns
    - Provides context assembly for LLM synthesis
    
    This is a "simulation" agent - it implements the agent pattern without
    requiring the full Agno framework. In production, this would coordinate
    with a cache and potentially multiple loader instances.
    """
    
    def __init__(self, budget_tokens: int = 4000):
        """
        Initialize the Loader Agent.
        
        Args:
            budget_tokens: Maximum tokens allowed in context (default: 4000)
        """
        self.budget = budget_tokens
        self.loaded_sections: Dict[Tuple[str, str], Dict] = {}
        self.current_usage = 0
        self.load_history: List[Tuple[str, str, str]] = []  # (action, file_id, section_id)
        self.thrash_count = 0
    
    def request_load(
        self,
        file_id: str,
        section_id: str,
        content: str,
        token_estimate: int,
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Attempt to load a section into context.
        
        Reference: AJrag.txt §5.3 - REQUEST_LOAD verb
        
        This simulates the REQUEST_LOAD verb from the design. It:
        1. Checks if the section would exceed the budget
        2. If yes, returns False with a reason
        3. If no, loads the section and returns True
        
        Args:
            file_id: The file ID of the section
            section_id: The section ID
            content: The text content to load
            token_estimate: Estimated tokens for this section
            metadata: Optional metadata about the section
        
        Returns:
            Tuple of (success: bool, reason: str)
        """
        key = (file_id, section_id)
        
        # Check if already loaded
        if key in self.loaded_sections:
            return True, f"Section {section_id} already loaded"
        
        # Check budget
        if self.current_usage + token_estimate > self.budget:
            return False, (
                f"Budget exceeded. Current: {self.current_usage}, "
                f"Requested: {token_estimate}, Budget: {self.budget}"
            )
        
        # Load the section
        self.loaded_sections[key] = {
            'content': content,
            'token_estimate': token_estimate,
            'metadata': metadata or {}
        }
        self.current_usage += token_estimate
        self.load_history.append(('LOAD', file_id, section_id))
        
        return True, f"Loaded {section_id} ({token_estimate} tokens)"
    
    def release(self, file_id: str, section_id: str) -> Tuple[bool, str]:
        """
        Release a section from context.
        
        Reference: AJrag.txt §5.3 - RELEASE verb
        
        This simulates the RELEASE verb from the design. It:
        1. Removes the section from loaded context
        2. Updates token usage
        3. Tracks the release in history (for thrash detection)
        
        Args:
            file_id: The file ID of the section
            section_id: The section ID
        
        Returns:
            Tuple of (success: bool, reason: str)
        """
        key = (file_id, section_id)
        
        if key not in self.loaded_sections:
            return False, f"Section {section_id} not loaded"
        
        # Check for thrash (releasing something we just loaded)
        if len(self.load_history) > 0:
            last_action, last_file, last_section = self.load_history[-1]
            if last_action == 'LOAD' and last_file == file_id and last_section == section_id:
                self.thrash_count += 1
        
        # Release the section
        section_data = self.loaded_sections[key]
        self.current_usage -= section_data['token_estimate']
        del self.loaded_sections[key]
        self.load_history.append(('RELEASE', file_id, section_id))
        
        return True, f"Released {section_id} ({section_data['token_estimate']} tokens)"
    
    def get_context(self, format: str = 'plain') -> str:
        """
        Get all loaded sections as a single context string.
        
        This assembles the context for the LLM. Sections are formatted
        with their section_id and label for citation purposes.
        
        Args:
            format: Output format ('plain' or 'structured')
        
        Returns:
            Assembled context string
        """
        if format == 'structured':
            return self._get_structured_context()
        else:
            return self._get_plain_context()
    
    def _get_plain_context(self) -> str:
        """
        Get context as plain text with section markers.
        
        Format:
        [section_id] Label
        Content
        
        [next_section_id] Next Label
        Next Content
        """
        context_parts = []
        for (file_id, section_id), data in self.loaded_sections.items():
            label = data['metadata'].get('label', section_id)
            context_parts.append(
                f"[{section_id}] {label}\n{data['content']}"
            )
        return "\n\n".join(context_parts)
    
    def _get_structured_context(self) -> str:
        """
        Get context as structured JSON-like format.
        
        This is useful for more advanced LLM prompting.
        """
        import json
        sections = []
        for (file_id, section_id), data in self.loaded_sections.items():
            sections.append({
                'file_id': file_id,
                'section_id': section_id,
                'label': data['metadata'].get('label', section_id),
                'content': data['content']
            })
        return json.dumps(sections, indent=2)
    
    def get_loaded_section_ids(self) -> List[str]:
        """
        Get a list of all loaded section IDs.
        
        This is useful for generating citations.
        
        Returns:
            List of section_id strings
        """
        return [section_id for (_, section_id) in self.loaded_sections.keys()]
    
    def get_budget_status(self) -> Dict:
        """
        Get current budget status.
        
        Returns:
            Dictionary with budget information
        """
        return {
            'budget': self.budget,
            'current_usage': self.current_usage,
            'remaining': self.budget - self.current_usage,
            'utilization': self.current_usage / self.budget if self.budget > 0 else 0,
            'sections_loaded': len(self.loaded_sections),
            'thrash_count': self.thrash_count
        }
    
    def calculate_thrash_rate(self) -> float:
        """
        Calculate the context thrash rate.
        
        Reference: AJrag.txt §2.2 Step 5 - "context thrash < 5%"
        
        Thrash occurs when sections are loaded and then immediately
        released, indicating poor routing decisions.
        
        Returns:
            Thrash rate as a percentage (0.0 to 1.0)
        """
        if len(self.load_history) == 0:
            return 0.0
        
        return self.thrash_count / len(self.load_history)
    
    def clear(self):
        """
        Clear all loaded sections and reset state.
        
        This is useful for starting a new query.
        """
        self.loaded_sections.clear()
        self.current_usage = 0
        # Don't clear history - we want to track thrash across queries
    
    def get_load_trace(self) -> str:
        """
        Get a human-readable trace of load/release operations.
        
        This is useful for debugging and understanding context management.
        
        Returns:
            String describing the load history
        """
        trace_lines = [
            "Loader Agent Trace",
            f"Budget: {self.budget} tokens",
            f"Current Usage: {self.current_usage} tokens ({self.current_usage / self.budget * 100:.1f}%)",
            f"Thrash Rate: {self.calculate_thrash_rate() * 100:.1f}%",
            "",
            "Load History:"
        ]
        
        for i, (action, file_id, section_id) in enumerate(self.load_history[-10:], 1):
            trace_lines.append(f"{i}. {action}: {file_id}/{section_id}")
        
        return "\n".join(trace_lines)


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    
    This is a simple heuristic: ~4 characters per token for English text.
    In production, this would use a proper tokenizer (e.g., tiktoken).
    
    Args:
        text: The text to estimate
    
    Returns:
        Estimated token count
    """
    return len(text) // 4
