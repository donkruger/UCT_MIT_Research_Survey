"""
Survey specification registry.

This module provides a registry for survey specifications.
New survey specs can be added by importing them and adding to the SPECS dictionary.
"""

# Import survey specifications here
from . import investment_research

# Registry of all available survey specifications
SPECS = {
    # Research surveys
    "investment_research": investment_research.SPEC,
}