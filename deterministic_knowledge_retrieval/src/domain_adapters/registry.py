"""
Domain Adapter Registry

Central registry for all domain adapters.
Automatically selects the right adapter based on source type or explicit domain.

Reference: domain_agnostic_knowledge_pack.md - Pluggable adapters
"""

from typing import Dict, Optional, Type
from .base_adapter import BaseDomainAdapter
from .healthcare_adapter import HealthcareAdapter
from .generic_adapter import GenericJSONAdapter


class AdapterRegistry:
    """
    Registry for domain adapters.
    
    This provides:
    1. Automatic adapter selection based on source
    2. Explicit adapter selection by domain name
    3. Fallback to generic adapter
    """
    
    def __init__(self):
        self._adapters: Dict[str, Type[BaseDomainAdapter]] = {}
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """Register built-in adapters."""
        self.register('healthcare', HealthcareAdapter)
        self.register('generic', GenericJSONAdapter)
    
    def register(self, domain_name: str, adapter_class: Type[BaseDomainAdapter]):
        """
        Register a new domain adapter.
        
        Args:
            domain_name: Name of the domain
            adapter_class: Adapter class (must inherit from BaseDomainAdapter)
        """
        self._adapters[domain_name] = adapter_class
    
    def get_adapter(self, domain_name: Optional[str] = None) -> BaseDomainAdapter:
        """
        Get an adapter instance.
        
        Args:
            domain_name: Optional domain name. If None, returns generic adapter.
        
        Returns:
            Adapter instance
        """
        if domain_name is None:
            domain_name = 'generic'
        
        if domain_name not in self._adapters:
            print(f"Warning: Unknown domain '{domain_name}', using generic adapter")
            domain_name = 'generic'
        
        adapter_class = self._adapters[domain_name]
        return adapter_class()
    
    def list_domains(self) -> list[str]:
        """
        List all registered domains.
        
        Returns:
            List of domain names
        """
        return list(self._adapters.keys())


# Global registry instance
_registry = AdapterRegistry()


def get_adapter(domain_name: Optional[str] = None) -> BaseDomainAdapter:
    """
    Get a domain adapter.
    
    Args:
        domain_name: Optional domain name
    
    Returns:
        Adapter instance
    """
    return _registry.get_adapter(domain_name)


def register_adapter(domain_name: str, adapter_class: Type[BaseDomainAdapter]):
    """
    Register a custom domain adapter.
    
    Args:
        domain_name: Name of the domain
        adapter_class: Adapter class
    """
    _registry.register(domain_name, adapter_class)


def list_domains() -> list[str]:
    """
    List all available domains.
    
    Returns:
        List of domain names
    """
    return _registry.list_domains()
