"""
Generic JSON Domain Adapter

This adapter handles any JSON source that follows a simple structure.
It's the fallback for domains without specialized adapters.

Reference: domain_agnostic_knowledge_pack.md - Universal Knowledge Pack
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from .base_adapter import BaseDomainAdapter


class GenericJSONAdapter(BaseDomainAdapter):
    """
    Generic adapter for any JSON knowledge source.
    
    Expects JSON with structure:
    {
      "dataset_id": "...",
      "sections": [
        {
          "id": "...",
          "title": "...",
          "content": "...",
          "metadata": {...}
        }
      ]
    }
    
    Or auto-detects structure and extracts sections.
    """
    
    def __init__(self, domain_name: str = "generic"):
        super().__init__(domain_name=domain_name)
    
    def extract_sections(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from generic JSON.
        
        Args:
            source_path: Path to JSON file
        
        Returns:
            List of sections
        """
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Try to detect structure
        if 'sections' in data:
            return self._extract_from_sections_array(data, source_path)
        elif isinstance(data, list):
            return self._extract_from_array(data, source_path)
        elif isinstance(data, dict):
            return self._extract_from_object(data, source_path)
        else:
            raise ValueError(f"Unsupported JSON structure in {source_path}")
    
    def _extract_from_sections_array(
        self,
        data: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract from {sections: [...]} structure."""
        file_id = data.get('dataset_id', Path(source_path).stem)
        sections = []
        
        for idx, section in enumerate(data['sections']):
            sections.append({
                'file_id': file_id,
                'section_id': section.get('id', f'sec_{idx}'),
                'label': section.get('title', section.get('label', f'Section {idx}')),
                'text': section.get('content', section.get('text', '')),
                'entities': section.get('entities', []),
                'metadata': section.get('metadata', {})
            })
        
        return sections
    
    def _extract_from_array(
        self,
        data: List[Dict[str, Any]],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract from array of objects."""
        file_id = Path(source_path).stem
        sections = []
        
        for idx, item in enumerate(data):
            # Try to find text content
            text = (
                item.get('content') or
                item.get('text') or
                item.get('description') or
                str(item)
            )
            
            sections.append({
                'file_id': file_id,
                'section_id': item.get('id', f'item_{idx}'),
                'label': item.get('title', item.get('name', f'Item {idx}')),
                'text': text,
                'entities': item.get('entities', []),
                'metadata': item
            })
        
        return sections
    
    def _extract_from_object(
        self,
        data: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract from single object (treat as one section)."""
        file_id = Path(source_path).stem
        
        # Try to find text content
        text = (
            data.get('content') or
            data.get('text') or
            data.get('description') or
            json.dumps(data, indent=2)
        )
        
        return [{
            'file_id': file_id,
            'section_id': data.get('id', 'main'),
            'label': data.get('title', data.get('name', file_id)),
            'text': text,
            'entities': data.get('entities', []),
            'metadata': data
        }]
    
    def enrich_metadata(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich with basic metadata.
        
        For generic sources, we do minimal enrichment:
        - Extract keywords from text
        - No domain-specific aliases
        
        Args:
            sections: Extracted sections
        
        Returns:
            Enriched sections
        """
        for section in sections:
            # Add basic aliases (just the label)
            if 'aliases' not in section:
                section['aliases'] = [section['label']]
            
            # Ensure entities list exists
            if 'entities' not in section:
                section['entities'] = []
        
        return sections
    
    def get_supported_formats(self) -> List[str]:
        """
        Get supported file formats.
        
        Returns:
            List of extensions
        """
        return ['.json', '.jsonl']
