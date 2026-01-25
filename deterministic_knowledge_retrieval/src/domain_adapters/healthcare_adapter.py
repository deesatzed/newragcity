"""
Healthcare Domain Adapter

This adapter handles medical/healthcare knowledge sources.
It wraps the existing infection document logic and makes it pluggable.
"""

from typing import List, Dict, Any
from .base_adapter import BaseDomainAdapter
from ..data_loader import load_infection_documents


class HealthcareAdapter(BaseDomainAdapter):
    """
    Adapter for healthcare/medical knowledge sources.
    
    Handles:
    - Infection disease documents
    - Clinical guidelines
    - Medical protocols
    - Drug information
    """
    
    def __init__(self):
        super().__init__(domain_name="healthcare")
    
    def extract_sections(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from healthcare documents.
        
        Currently supports infection disease JSON format.
        
        Args:
            source_path: Path to JSON file
        
        Returns:
            List of sections
        """
        # Use existing loader
        sections, warnings = load_infection_documents([source_path])
        
        # Log warnings if any
        if warnings:
            print(f"Healthcare adapter warnings: {warnings}")
        
        return sections
    
    def enrich_metadata(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich with healthcare-specific metadata.
        
        The existing loader already does this (entities, aliases).
        This is a pass-through for now.
        
        Args:
            sections: Extracted sections
        
        Returns:
            Enriched sections
        """
        # Existing loader already enriches with entities and aliases
        return sections
    
    def get_supported_formats(self) -> List[str]:
        """
        Get supported file formats.
        
        Returns:
            List of extensions
        """
        return ['.json']
