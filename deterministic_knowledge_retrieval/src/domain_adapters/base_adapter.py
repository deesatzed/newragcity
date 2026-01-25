"""
Base Domain Adapter: Universal interface for any knowledge source

Reference: domain_agnostic_knowledge_pack.md - Converter Adapters

This module defines the interface that all domain adapters must implement.
The goal is to convert ANY source (healthcare, finance, policy, code, etc.)
into the Universal Knowledge Pack (UKP) format.

Key Responsibilities:
1. Define the adapter interface
2. Provide base validation logic
3. Ensure lossless extraction (no summarization)
4. Generate consistent metadata
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path


class BaseDomainAdapter(ABC):
    """
    Abstract base class for domain adapters.
    
    Each domain (healthcare, finance, policy, etc.) implements this interface
    to convert its sources into the Universal Knowledge Pack format.
    
    Design Principles:
    - Lossless extraction only (no summarization)
    - Deterministic output (same input → same output)
    - Minimal metadata (just what's needed for routing)
    - Domain-agnostic schema
    """
    
    def __init__(self, domain_name: str):
        """
        Initialize the adapter.
        
        Args:
            domain_name: Name of the domain (e.g., "healthcare", "finance")
        """
        self.domain_name = domain_name
    
    @abstractmethod
    def extract_sections(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a source file.
        
        This is the main extraction method. It must:
        1. Parse the source file (JSON, PDF, CSV, etc.)
        2. Break it into addressable sections
        3. Return sections in UKP format
        
        Args:
            source_path: Path to the source file
        
        Returns:
            List of section dictionaries with:
            - file_id: Unique identifier for the source
            - section_id: Unique identifier for this section
            - label: Human-readable label
            - text: The section content (lossless)
            - entities: List of key entities (optional)
            - metadata: Domain-specific metadata (optional)
        """
        pass
    
    @abstractmethod
    def enrich_metadata(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich sections with domain-specific metadata.
        
        This adds:
        - Aliases (synonyms, abbreviations)
        - Entities (key terms, concepts)
        - Tags (categories, topics)
        - Any domain-specific fields
        
        Args:
            sections: List of extracted sections
        
        Returns:
            List of enriched sections
        """
        pass
    
    def validate_section(self, section: Dict[str, Any]) -> bool:
        """
        Validate that a section meets UKP requirements.
        
        Required fields:
        - file_id
        - section_id
        - label
        - text
        
        Args:
            section: Section dictionary
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['file_id', 'section_id', 'label', 'text']
        return all(field in section for field in required_fields)
    
    def get_domain_info(self) -> Dict[str, Any]:
        """
        Get information about this domain adapter.
        
        Returns:
            Dictionary with adapter metadata
        """
        return {
            'domain': self.domain_name,
            'adapter_version': '1.0.0',
            'supported_formats': self.get_supported_formats()
        }
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of file extensions (e.g., ['.json', '.pdf'])
        """
        pass
