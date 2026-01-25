"""
LLM provider abstraction for answer synthesis.

Supports multiple backends: OpenAI, Anthropic, Ollama (local).
Each provider implements a simple generate() interface.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(
        self,
        query: str,
        context: str,
        citations: List[str],
        max_tokens: int = 500,
    ) -> str:
        """Generate an answer from query and context."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def generate(
        self,
        query: str,
        context: str,
        citations: List[str],
        max_tokens: int = 500,
    ) -> str:
        prompt = self._build_prompt(query, context, citations)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise assistant. Answer using only the provided context. Always cite sources using [section_id] format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.1,  # Low temperature for factual responses
        )
        
        return response.choices[0].message.content or ""
    
    @staticmethod
    def _build_prompt(query: str, context: str, citations: List[str]) -> str:
        return f"""Context (with citations):
{context}

Available citations: {', '.join(citations)}

Question: {query}

Provide a clear, direct answer using only the information from the context above. Cite sources using [section_id] format."""


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, model: str = "claude-3-5-haiku-20241022", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    def generate(
        self,
        query: str,
        context: str,
        citations: List[str],
        max_tokens: int = 500,
    ) -> str:
        prompt = OpenAIProvider._build_prompt(query, context, citations)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=0.1,
            system="You are a precise assistant. Answer using only the provided context. Always cite sources using [section_id] format.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text if response.content else ""


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("Requests package not installed. Run: pip install requests")
    
    def generate(
        self,
        query: str,
        context: str,
        citations: List[str],
        max_tokens: int = 500,
    ) -> str:
        prompt = OpenAIProvider._build_prompt(query, context, citations)
        system_prompt = "You are a precise assistant. Answer using only the provided context. Always cite sources using [section_id] format."
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": max_tokens,
                }
            },
            timeout=60,
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise RuntimeError(f"Ollama API error: {response.status_code} - {response.text}")


class MockProvider(LLMProvider):
    """Mock provider for testing (no API calls)."""
    
    def generate(
        self,
        query: str,
        context: str,
        citations: List[str],
        max_tokens: int = 500,
    ) -> str:
        # Return a simple formatted response for testing
        return f"Mock answer to: {query}\n\nBased on context from: {', '.join(citations)}"


def create_provider(provider_type: str = "mock", **kwargs) -> LLMProvider:
    """
    Factory function to create LLM providers.
    
    Args:
        provider_type: One of 'openai', 'anthropic', 'ollama', 'mock'
        **kwargs: Provider-specific configuration
    
    Returns:
        LLMProvider instance
    
    Examples:
        >>> provider = create_provider("openai", model="gpt-4o-mini")
        >>> provider = create_provider("anthropic", model="claude-3-5-haiku-20241022")
        >>> provider = create_provider("ollama", model="llama3.2:3b")
        >>> provider = create_provider("mock")  # For testing
    """
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "mock": MockProvider,
    }
    
    if provider_type not in providers:
        raise ValueError(
            f"Unknown provider: {provider_type}. Choose from: {', '.join(providers.keys())}"
        )
    
    return providers[provider_type](**kwargs)
