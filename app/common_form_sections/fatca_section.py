"""
FATCA Section Component

Component for capturing FATCA classification and related information.
Implements the complete FATCA classification tree with conditional field rendering.
"""

import streamlit as st
from typing import List, Dict, Any
from app.common_form_sections.base import SectionComponent
from app.utils import inst_key, persist_selectbox, persist_text_input, persist_checkbox
from app.controlled_lists_enhanced import (
    get_fatca_classifications_with_descriptions, 
    get_us_person_types_with_descriptions, 
    get_ffi_categories_with_descriptions, 
    get_nffe_types_with_descriptions
)
from .compliance_helpers import (
    render_giin_section, 
    render_controlling_person_section,
    validate_controlling_person_section,
    serialize_controlling_person_section,
    get_fatca_validation_errors
)


class FatcaSectionComponent(SectionComponent):
    """
    Component for capturing FATCA classification and related information.
    
    Config (kwargs):
      - title: str = "FATCA Classification" (section heading)
      - required: bool = True (whether section is mandatory)
    """
    
    def render(self, *, ns: str, instance_id: str, **config) -> None:
        """Render the FATCA section with conditional field logic."""
        title = config.get("title", "FATCA Classification")
        st.subheader(title)
        
        # Top-level FATCA Classification (always required)
        classification_key = inst_key(ns, instance_id, "fatca_classification")
        
        # Get the mapping of codes to their descriptive labels
        fatca_options = get_fatca_classifications_with_descriptions()
        
        # Add blank option at the beginning and include the valid codes
        fatca_codes = ["", "US_PERSON", "FFI", "NFFE"]
        
        # Create display options with blank first option
        display_options = ["-- Please select a FATCA Classification --"]
        display_options.extend(fatca_options)
        
        # Don't initialize with a default value - let it remain empty
        # This ensures the user must actively select an option
        
        # Use format_func to display rich text while storing the clean code
        classification = persist_selectbox(
            "FATCA Classification",
            classification_key,
            options=fatca_codes,
            format_func=lambda code: display_options[fatca_codes.index(code)] if code in fatca_codes else code,
            help="Select the appropriate FATCA classification for this entity (required)"
        )
        
        # Conditional rendering based on FATCA Classification
        # Only render sub-sections if a valid classification is selected
        if classification == "US_PERSON":
            self._render_us_person_section(ns, instance_id)
        elif classification == "FFI":
            self._render_ffi_section(ns, instance_id)
        elif classification == "NFFE":
            self._render_nffe_section(ns, instance_id)
    
    def _render_us_person_section(self, ns: str, instance_id: str) -> None:
        """Render US Person specific fields."""
        st.markdown("**US Person Details**")
        
        # US Person Type
        us_person_type_key = inst_key(ns, instance_id, "us_person_type")
        
        # Get the mapping of codes to their descriptive labels
        us_person_options = get_us_person_types_with_descriptions()
        us_person_codes = ["SPECIFIED_US_PERSON", "NON_SPECIFIED_US_PERSON"]
        
        # Don't initialize with a default - let user select
        
        # Use format_func to display rich text while storing the clean code
        us_person_type = persist_selectbox(
            "US Person Type",
            us_person_type_key,
            options=us_person_codes,
            format_func=lambda code: us_person_options[us_person_codes.index(code)] if code in us_person_codes else code
        )
        
        # US TIN (only for Specified US Person)
        if us_person_type == "SPECIFIED_US_PERSON":
            us_tin_key = inst_key(ns, instance_id, "us_tin")
            persist_text_input(
                "US TIN (Tax Identification Number)",
                us_tin_key,
                help="Enter the 9-11 digit US Tax Identification Number (e.g., 123-45-6789)"
            )
    
    def _render_ffi_section(self, ns: str, instance_id: str) -> None:
        """Render Foreign Financial Institution specific fields."""
        st.markdown("**FFI Details**")
        
        # FFI Category
        ffi_category_key = inst_key(ns, instance_id, "ffi_category")
        
        # Get the mapping of codes to their descriptive labels
        ffi_options = get_ffi_categories_with_descriptions()
        ffi_codes = ["REPORTING_FFI", "REGISTERED_DEEMED_COMPLIANT", "NON_REPORTING_FFI", "EXEMPT_BENEFICIAL_OWNER", "NON_PARTICIPATING_FFI", "CERTIFIED_DEEMED_COMPLIANT"]
        
        # Don't initialize with a default - let user select
        
        # Use format_func to display rich text while storing the clean code
        ffi_category = persist_selectbox(
            "FFI Category",
            ffi_category_key,
            options=ffi_codes,
            format_func=lambda code: ffi_options[ffi_codes.index(code)] if code in ffi_codes else code
        )
        
        # GIIN and Sponsor fields for Reporting FFI and Registered Deemed-Compliant FFI
        if ffi_category in ["REPORTING_FFI", "REGISTERED_DEEMED_COMPLIANT"]:
            render_giin_section(ns, instance_id, "FFI GIIN Information")
    
    def _render_nffe_section(self, ns: str, instance_id: str) -> None:
        """Render Non-Financial Foreign Entity specific fields."""
        st.markdown("**NFFE Details**")
        
        # NFFE Type
        nffe_type_key = inst_key(ns, instance_id, "nffe_type")
        
        # Get the mapping of codes to their descriptive labels
        nffe_options = get_nffe_types_with_descriptions()
        nffe_codes = ["ACTIVE_NFFE", "PASSIVE_NFFE", "DIRECT_REPORTING_NFFE"]
        
        # Don't initialize with a default - let user select
        
        # Use format_func to display rich text while storing the clean code
        nffe_type = persist_selectbox(
            "NFFE Type",
            nffe_type_key,
            options=nffe_codes,
            format_func=lambda code: nffe_options[nffe_codes.index(code)] if code in nffe_codes else code
        )
        
        if nffe_type == "PASSIVE_NFFE":
            # Render Controlling Person section for Passive NFFE
            render_controlling_person_section(
                ns, instance_id, 
                self._get_component_registry(),
                "Controlling Person Information (Required for Passive NFFE)"
            )
        elif nffe_type == "DIRECT_REPORTING_NFFE":
            # GIIN and Sponsor fields for Direct-Reporting NFFE
            render_giin_section(ns, instance_id, "Direct-Reporting NFFE GIIN Information")
    
    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        """Validate FATCA section data."""
        errors = []
        
        # Get component registry for validation
        component_registry = self._get_component_registry()
        
        # Validate FATCA-specific rules
        errors.extend(get_fatca_validation_errors(ns, instance_id))
        
        # Validate controlling person section if present
        fatca_class = st.session_state.get(inst_key(ns, instance_id, "fatca_classification"), "")
        if fatca_class == "NFFE":
            nffe_type = st.session_state.get(inst_key(ns, instance_id, "nffe_type"), "")
            if nffe_type == "PASSIVE_NFFE":
                errors.extend(validate_controlling_person_section(ns, instance_id, component_registry))
        
        return errors
    
    def serialize(self, *, ns: str, instance_id: str, **config) -> tuple[Dict[str, Any], List[Any]]:
        """Serialize FATCA section data for export."""
        payload = {}
        uploads = []
        
        # Get component registry for serialization
        component_registry = self._get_component_registry()
        
        # Basic FATCA classification
        fatca_class = st.session_state.get(inst_key(ns, instance_id, "fatca_classification"), "")
        if fatca_class:
            payload["FATCA Classification"] = fatca_class
        
        # US Person specific data
        if fatca_class == "US_PERSON":
            us_person_type = st.session_state.get(inst_key(ns, instance_id, "us_person_type"), "")
            if us_person_type:
                payload["US Person Type"] = us_person_type
            
            if us_person_type == "SPECIFIED_US_PERSON":
                us_tin = st.session_state.get(inst_key(ns, instance_id, "us_tin"), "")
                if us_tin:
                    payload["US TIN"] = us_tin
        
        # FFI specific data
        elif fatca_class == "FFI":
            ffi_category = st.session_state.get(inst_key(ns, instance_id, "ffi_category"), "")
            if ffi_category:
                payload["FFI Category"] = ffi_category
            
            if ffi_category in ["REPORTING_FFI", "REGISTERED_DEEMED_COMPLIANT"]:
                giin = st.session_state.get(inst_key(ns, instance_id, "giin"), "")
                if giin:
                    payload["GIIN"] = giin
                
                is_sponsor = st.session_state.get(inst_key(ns, instance_id, "is_giin_of_sponsor"), False)
                payload["Is GIIN of Sponsoring Entity"] = "Yes" if is_sponsor else "No"
                
                if is_sponsor:
                    sponsor_name = st.session_state.get(inst_key(ns, instance_id, "sponsor_name"), "")
                    if sponsor_name:
                        payload["Sponsor Name"] = sponsor_name
        
        # NFFE specific data
        elif fatca_class == "NFFE":
            nffe_type = st.session_state.get(inst_key(ns, instance_id, "nffe_type"), "")
            if nffe_type:
                payload["NFFE Type"] = nffe_type
            
            if nffe_type == "PASSIVE_NFFE":
                # Serialize controlling person data
                cp_payload, cp_uploads = serialize_controlling_person_section(ns, instance_id, component_registry)
                payload.update(cp_payload)
                uploads.extend(cp_uploads)
            
            elif nffe_type == "DIRECT_REPORTING_NFFE":
                giin = st.session_state.get(inst_key(ns, instance_id, "giin"), "")
                if giin:
                    payload["GIIN"] = giin
                
                is_sponsor = st.session_state.get(inst_key(ns, instance_id, "is_giin_of_sponsor"), False)
                payload["Is GIIN of Sponsoring Entity"] = "Yes" if is_sponsor else "No"
                
                if is_sponsor:
                    sponsor_name = st.session_state.get(inst_key(ns, instance_id, "sponsor_name"), "")
                    if sponsor_name:
                        payload["Sponsor Name"] = sponsor_name
        
        return payload, uploads
    
    def _get_component_registry(self):
        """Get the component registry for accessing other components."""
        # Import here to avoid circular imports
        from app.common_form_sections import get_component_registry
        return get_component_registry()
