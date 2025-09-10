"""
Compliance Helpers for FATCA and CRS Components

This module provides shared validation and rendering functions for FATCA and CRS sections
to maintain the DRY principle and ensure consistency across components.
"""

import re
import streamlit as st
from typing import List
from app.utils import persist_text_input, persist_selectbox, persist_checkbox, inst_key



def validate_giin(giin: str) -> bool:
    """
    Validate GIIN format: XXXXXX.XXXXX.XX.XXX
    
    Args:
        giin: The GIIN string to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not giin:
        return False
    
    # Check pattern: 6.5.2.3 characters separated by dots
    pattern = r'^[A-Z0-9]{6}\.[A-Z0-9]{5}\.[A-Z0-9]{2}\.[A-Z0-9]{3}$'
    return bool(re.match(pattern, giin))


def validate_us_tin(tin: str) -> bool:
    """
    Validate US TIN format (9-11 digits, hyphens allowed)
    
    Args:
        tin: The US TIN string to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not tin:
        return False
    
    # Remove hyphens and check if all digits
    clean_tin = re.sub(r'[^0-9]', '', tin)
    return len(clean_tin) in [9, 10, 11] and clean_tin.isdigit()


def render_giin_section(ns: str, instance_id: str, title: str = "GIIN Information") -> None:
    """
    Renders the common GIIN and Sponsor Name fields.
    
    Args:
        ns: Entity namespace
        instance_id: Component instance identifier
        title: Section title for the GIIN information
    """
    st.markdown(f"**{title}**")
    
    # Introductory callout aligned with Getting Started styling
    st.markdown(
        """
<div class="callout-info">
  <p><strong>Complete information for each controlling person as required by FATCA/CRS regulations.</strong></p>
  <p>Provide accurate details to avoid delays in processing.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    # GIIN field
    giin_key = inst_key(ns, instance_id, "giin")
    persist_text_input(
        "GIIN (Global Intermediary Identification Number)", 
        giin_key,
        help="Format: XXXXXX.XXXXX.XX.XXX (e.g., ABCDEF.12345.AB.123)"
    )
    
    # Sponsor entity checkbox
    is_sponsor_key = inst_key(ns, instance_id, "is_giin_of_sponsor")
    is_sponsor = persist_checkbox(
        "Is the GIIN provided above that of a Sponsoring Entity?", 
        is_sponsor_key
    )
    
    # Sponsor name field (conditional)
    if is_sponsor:
        sponsor_name_key = inst_key(ns, instance_id, "sponsor_name")
        persist_text_input("Sponsor's Name", sponsor_name_key)


def render_controlling_person_section(ns: str, instance_id: str, 
                                    component_registry, title: str = "Controlling Person Information") -> None:
    """
    Renders the controlling person section using the dedicated controlling_person component.
    
    Args:
        ns: Entity namespace
        instance_id: Component instance identifier
        component_registry: Component registry to get controlling_person component
        title: Section title for controlling person information
    """
    # Get the dedicated controlling_person component
    cp_component = component_registry.get("controlling_person")
    if cp_component:
        cp_instance_id = f"{instance_id}_controlling_persons"
        cp_config = {
            "title": title,
            "role_label": "Controlling Person",
            "min_count": 1,
            "help_text": "Complete information for each controlling person as required by FATCA/CRS regulations."
        }
        cp_component.render(ns=ns, instance_id=cp_instance_id, **cp_config)
    else:
        st.error("Controlling Person component not available")


def validate_controlling_person_section(ns: str, instance_id: str, 
                                      component_registry) -> List[str]:
    """
    Validates the controlling person section.
    
    Args:
        ns: Entity namespace
        instance_id: Component instance identifier
        component_registry: Component registry to get controlling_person component
        
    Returns:
        List[str]: List of validation error messages
    """
    errors = []
    
    # Get the dedicated controlling_person component
    cp_component = component_registry.get("controlling_person")
    if cp_component:
        cp_instance_id = f"{instance_id}_controlling_persons"
        cp_config = {
            "role_label": "Controlling Person",
            "min_count": 1
        }
        errors.extend(cp_component.validate(ns=ns, instance_id=cp_instance_id, **cp_config))
    else:
        errors.append("Controlling Person component not available")
    
    return errors


def serialize_controlling_person_section(ns: str, instance_id: str, 
                                       component_registry) -> tuple[dict, list]:
    """
    Serializes the controlling person section data.
    
    Args:
        ns: Entity namespace
        instance_id: Component instance identifier
        component_registry: Component registry to get controlling_person component
        
    Returns:
        tuple[dict, list]: (payload_dict, uploads_list)
        
    Note: Returns controlling person data directly as "Controlling Persons" section
    to ensure proper CSV flattening with individual fields per row.
    """
    payload = {}
    uploads = []
    
    # Get the dedicated controlling_person component
    cp_component = component_registry.get("controlling_person")
    if cp_component:
        cp_instance_id = f"{instance_id}_controlling_persons"
        cp_config = {
            "role_label": "Controlling Person",
            "min_count": 1
        }
        cp_payload, cp_uploads = cp_component.serialize(ns=ns, instance_id=cp_instance_id, **cp_config)
        # Return the controlling person data directly as "Controlling Persons" section
        # This ensures the CSV generator processes it as a collection with Records
        payload["Controlling Persons"] = cp_payload
        uploads.extend(cp_uploads)
    else:
        payload["Controlling Persons"] = {"Count": 0, "Records": [], "Error": "Component not available"}
    
    return payload, uploads


def get_fatca_validation_errors(ns: str, instance_id: str) -> List[str]:
    """
    Get FATCA-specific validation errors based on current selections.
    
    Args:
        ns: Entity namespace
        instance_id: Component instance identifier
        
    Returns:
        List[str]: List of validation error messages
    """
    errors = []
    
    # Get current FATCA classification
    fatca_class = st.session_state.get(inst_key(ns, instance_id, "fatca_classification"), "")
    
    if not fatca_class:
        errors.append("FATCA Classification is required.")
        return errors
    
    # Validate US Person specific fields
    if fatca_class == "US_PERSON":
        us_person_type = st.session_state.get(inst_key(ns, instance_id, "us_person_type"), "")
        if not us_person_type:
            errors.append("US Person Type is required when FATCA Classification is US Person.")
        
        if us_person_type == "SPECIFIED_US_PERSON":
            us_tin = st.session_state.get(inst_key(ns, instance_id, "us_tin"), "")
            if not us_tin or not validate_us_tin(us_tin):
                errors.append("Valid US TIN is required for Specified US Person.")
    
    # Validate FFI specific fields
    elif fatca_class == "FFI":
        ffi_category = st.session_state.get(inst_key(ns, instance_id, "ffi_category"), "")
        if not ffi_category:
            errors.append("FFI Category is required when FATCA Classification is FFI.")
        
        if ffi_category in ["REPORTING_FFI", "REGISTERED_DEEMED_COMPLIANT"]:
            giin = st.session_state.get(inst_key(ns, instance_id, "giin"), "")
            if not giin or not validate_giin(giin):
                errors.append("Valid GIIN is required for Reporting FFI or Registered Deemed-Compliant FFI.")
            
            is_sponsor = st.session_state.get(inst_key(ns, instance_id, "is_giin_of_sponsor"), False)
            if is_sponsor:
                sponsor_name = st.session_state.get(inst_key(ns, instance_id, "sponsor_name"), "")
                if not sponsor_name.strip():
                    errors.append("Sponsor Name is required when GIIN is of a Sponsoring Entity.")
    
    # Validate NFFE specific fields
    elif fatca_class == "NFFE":
        nffe_type = st.session_state.get(inst_key(ns, instance_id, "nffe_type"), "")
        if not nffe_type:
            errors.append("NFFE Type is required when FATCA Classification is NFFE.")
        
        if nffe_type == "DIRECT_REPORTING_NFFE":
            giin = st.session_state.get(inst_key(ns, instance_id, "giin"), "")
            if not giin or not validate_giin(giin):
                errors.append("Valid GIIN is required for Direct-Reporting NFFE.")
            
            is_sponsor = st.session_state.get(inst_key(ns, instance_id, "is_giin_of_sponsor"), False)
            if is_sponsor:
                sponsor_name = st.session_state.get(inst_key(ns, instance_id, "sponsor_name"), "")
                if not sponsor_name.strip():
                    errors.append("Sponsor Name is required when GIIN is of a Sponsoring Entity.")
    
    return errors


def get_crs_validation_errors(ns: str, instance_id: str) -> List[str]:
    """
    Get CRS-specific validation errors based on current selections.
    
    Args:
        ns: Entity namespace
        instance_id: Component instance identifier
        
    Returns:
        List[str]: List of validation error messages
    """
    errors = []
    
    # Get current CRS classification
    crs_class = st.session_state.get(inst_key(ns, instance_id, "crs_classification"), "")
    
    if not crs_class:
        errors.append("CRS Classification is required.")
        return errors
    
    # Validate Investment Entity specific fields
    if crs_class == "FI_INVESTMENT_ENTITY":
        investment_entity_type = st.session_state.get(inst_key(ns, instance_id, "investment_entity_type"), "")
        if not investment_entity_type:
            errors.append("Investment Entity Type is required when CRS Classification is Investment Entity.")
    
    # Validate Stock Exchange specific fields
    elif crs_class == "ACTIVE_NFE_STOCK_EXCHANGE":
        stock_exchange = st.session_state.get(inst_key(ns, instance_id, "stock_exchange_name"), "")
        if not stock_exchange.strip():
            errors.append("Stock Exchange Name is required when CRS Classification is Active NFE listed on stock exchange.")
        
        ticker_symbol = st.session_state.get(inst_key(ns, instance_id, "entity_ticker_symbol"), "")
        if not ticker_symbol.strip():
            errors.append("Entity Ticker/Symbol is required when CRS Classification is Active NFE listed on stock exchange.")
        
        related_entity = st.session_state.get(inst_key(ns, instance_id, "related_entity_regularly_traded"), False)
        if related_entity:
            parent_name = st.session_state.get(inst_key(ns, instance_id, "parent_entity_name"), "")
            if not parent_name.strip():
                errors.append("Parent Entity Name is required when related to regularly traded corporation.")
            
            parent_exchange = st.session_state.get(inst_key(ns, instance_id, "parent_entity_stock_exchange"), "")
            if not parent_exchange.strip():
                errors.append("Parent Entity stock exchange is required when related to regularly traded corporation.")
    
    return errors
