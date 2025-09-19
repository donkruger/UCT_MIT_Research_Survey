"""
Reusable form components for surveys.

This module provides a registry system for reusable form components.
Components implement the SectionComponent interface for consistent behavior.
"""

from typing import Dict
from app.common_form_sections.base import SectionComponent

# Global component registry
_REGISTRY: Dict[str, SectionComponent] = {}

def register_component(name: str, component: SectionComponent):
    """Register a reusable section under a stable name."""
    _REGISTRY[name] = component

def get_component(name: str) -> SectionComponent | None:
    """Retrieve a registered component by name."""
    return _REGISTRY.get(name)

def get_component_registry() -> Dict[str, SectionComponent]:
    """Get the complete component registry."""
    return _REGISTRY.copy()

# Auto-register components on import
from . import address
from . import phone

# Register all components
register_component("address", address.AddressComponent())
register_component("phone", phone.PhoneComponent())