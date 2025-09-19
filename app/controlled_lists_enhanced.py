"""
Enhanced controlled list management for surveys.

This module provides a flexible system for managing controlled lists with 
code/label separation and metadata support.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

class ControlledListManager:
    """Manager class for all controlled lists with structured data."""
    
    def __init__(self):
        self._controlled_lists = {}
        self._countries = self._load_countries_from_csv()
        self._country_dial_codes = self._load_country_dial_codes()
    
    def _load_countries_from_csv(self) -> List[str]:
        """Load country list from CSV file."""
        countries = [""]  # Start with empty option
        csv_path = Path(__file__).parent / "common_form_sections" / "CountryListV2.csv"
        
        if csv_path.exists():
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'Country Name' in row and row['Country Name']:
                            countries.append(row['Country Name'].strip())
            except Exception as e:
                print(f"Error loading countries: {e}")
        
        return countries
    
    def _load_country_dial_codes(self) -> List[str]:
        """Load country dialing codes from CSV file."""
        dial_codes = [""]  # Start with empty option
        csv_path = Path(__file__).parent / "common_form_sections" / "CountryListV2.csv"
        
        if csv_path.exists():
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    seen = set()
                    for row in reader:
                        if 'Dialing Code' in row and row['Dialing Code']:
                            code = row['Dialing Code'].strip()
                            if code not in seen:
                                dial_codes.append(code)
                                seen.add(code)
            except Exception as e:
                print(f"Error loading dialing codes: {e}")
        
        # Ensure +27 is second if present
        if "+27" in dial_codes:
            dial_codes.remove("+27")
            dial_codes.insert(1, "+27")
        
        return dial_codes
    
    def get_countries(self, include_empty: bool = True) -> List[str]:
        """Get list of countries."""
        if include_empty:
            return self._countries.copy()
        return [c for c in self._countries if c]
    
    def get_country_dial_codes(self, include_empty: bool = True) -> List[str]:
        """Get list of country dialing codes."""
        if include_empty:
            return self._country_dial_codes.copy()
        return [c for c in self._country_dial_codes if c]
    
    def add_controlled_list(self, name: str, items: List[Dict[str, Any]]):
        """Add a new controlled list."""
        self._controlled_lists[name] = items
    
    def get_list_options(self, list_name: str, include_empty: bool = True, 
                        return_codes: bool = False) -> List[str]:
        """Get options for a controlled list."""
        if list_name not in self._controlled_lists:
            return [""] if include_empty else []
        
        items = self._controlled_lists[list_name]
        result = []
        
        if include_empty:
            result.append("")
        
        for item in items:
            if isinstance(item, dict):
                if return_codes and 'code' in item:
                    result.append(item['code'])
                elif 'label' in item:
                    result.append(item['label'])
                else:
                    result.append(str(item))
            else:
                result.append(str(item))
        
        return result

# Global instance
_controlled_list_manager = ControlledListManager()

# Convenience functions
def get_countries(include_empty: bool = True) -> List[str]:
    """Get list of countries."""
    return _controlled_list_manager.get_countries(include_empty)

def get_country_dial_codes(include_empty: bool = True) -> List[str]:
    """Get list of country dialing codes."""
    return _controlled_list_manager.get_country_dial_codes(include_empty)