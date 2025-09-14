"""
CRS Section Component

Component for capturing CRS classification and related information.
Implements the complete CRS classification tree with conditional field rendering.
"""

import streamlit as st
from typing import List, Dict, Any
from app.common_form_sections.base import SectionComponent
from app.utils import inst_key, persist_selectbox, persist_text_input, persist_checkbox
from app.controlled_lists_enhanced import (
    get_crs_classifications_with_descriptions, 
    get_investment_entity_types_with_descriptions
)
from .compliance_helpers import (
    render_giin_section, 
    render_controlling_person_section,
    validate_controlling_person_section,
    serialize_controlling_person_section,
    get_crs_validation_errors
)


class CrsSectionComponent(SectionComponent):
    """
    Component for capturing CRS classification and related information.
    
    Config (kwargs):
      - title: str = "CRS Classification" (section heading)
      - required: bool = True (whether section is mandatory)
    """
    
    def render(self, *, ns: str, instance_id: str, **config) -> None:
        """Render the CRS section with conditional field logic."""
        title = config.get("title", "CRS Classification")
        st.subheader(title)
        
        # Top-level CRS Classification (always required)
        classification_key = inst_key(ns, instance_id, "crs_classification")
        
        # Get the mapping of codes to their descriptive labels
        crs_options = get_crs_classifications_with_descriptions()
        
        # Add blank option at the beginning and include the valid codes
        crs_codes = ["", "FI_INVESTMENT_ENTITY", "FI_DEPOSITORY_CUSTODIAL_INSURANCE", "NON_REPORTING_FI", "ACTIVE_NFE_STOCK_EXCHANGE", "OTHER_ACTIVE_NFE", "PASSIVE_NFE"]
        
        # Create display options with blank first option
        display_options = ["-- Please select a CRS Classification --"]
        display_options.extend(crs_options)
        
        # Don't initialize with a default value - let it remain empty
        # This ensures the user must actively select an option
        
        # Use format_func to display rich text while storing the clean code
        classification = persist_selectbox(
            "CRS Classification",
            classification_key,
            options=crs_codes,
            format_func=lambda code: display_options[crs_codes.index(code)] if code in crs_codes else code,
            help="Select the appropriate CRS classification for this entity (required)"
        )
        
        # Conditional rendering based on CRS Classification
        # Only render sub-sections if a valid classification is selected
        if classification == "FI_INVESTMENT_ENTITY":
            self._render_investment_entity_section(ns, instance_id)
        elif classification == "FI_DEPOSITORY_CUSTODIAL_INSURANCE":
            self._render_depository_custodial_insurance_section(ns, instance_id)
        elif classification == "NON_REPORTING_FI":
            self._render_non_reporting_fi_section(ns, instance_id)
        elif classification == "ACTIVE_NFE_STOCK_EXCHANGE":
            self._render_stock_exchange_section(ns, instance_id)
        elif classification == "OTHER_ACTIVE_NFE":
            self._render_other_active_nfe_section(ns, instance_id)
        elif classification == "PASSIVE_NFE":
            self._render_passive_nfe_section(ns, instance_id)
    
    def _render_investment_entity_section(self, ns: str, instance_id: str) -> None:
        """Render Investment Entity specific fields."""
        st.markdown("**Investment Entity Details**")
        
        # Investment Entity Type
        investment_entity_type_key = inst_key(ns, instance_id, "investment_entity_type")
        
        # Get the mapping of codes to their descriptive labels
        investment_options = get_investment_entity_types_with_descriptions()
        investment_codes = ["NON_PARTICIPATING_JURISDICTION", "OTHER_INVESTMENT_ENTITY"]
        
        # Don't initialize with a default - let user select
        
        # Use format_func to display rich text while storing the clean code
        investment_entity_type = persist_selectbox(
            "Investment Entity Type",
            investment_entity_type_key,
            options=investment_codes,
            format_func=lambda code: investment_options[investment_codes.index(code)] if code in investment_codes else code
        )
        
        # Controlling Person Information for non-participating jurisdiction entities
        if investment_entity_type == "NON_PARTICIPATING_JURISDICTION":
            render_controlling_person_section(
                ns, instance_id, 
                self._get_component_registry(),
                "Controlling Person Information (Required for Investment Entity in non-participating jurisdiction)"
            )
    
    def _render_stock_exchange_section(self, ns: str, instance_id: str) -> None:
        """Render Stock Exchange specific fields."""
        st.markdown("**Stock Exchange Details**")
        
        # Stock Exchange Name
        stock_exchange_key = inst_key(ns, instance_id, "stock_exchange_name")
        persist_text_input(
            "Stock Exchange Name",
            stock_exchange_key,
            help="Enter the name of the stock exchange where the entity is listed"
        )
        
        # Entity Ticker/Symbol
        ticker_symbol_key = inst_key(ns, instance_id, "entity_ticker_symbol")
        persist_text_input(
            "Entity Ticker/Symbol",
            ticker_symbol_key,
            help="Enter the ticker symbol or trading code for the entity"
        )
        
        # Related entity of regularly traded corporation
        related_entity_key = inst_key(ns, instance_id, "related_entity_regularly_traded")
        related_entity = persist_checkbox(
            "Are you a related entity of a regularly traded corporation?",
            related_entity_key
        )
        
        # Parent entity details (conditional)
        if related_entity:
            st.markdown("**Parent Entity Details**")
            
            parent_name_key = inst_key(ns, instance_id, "parent_entity_name")
            persist_text_input(
                "Parent Entity Name",
                parent_name_key,
                help="Enter the name of the parent entity"
            )
            
            parent_exchange_key = inst_key(ns, instance_id, "parent_entity_stock_exchange")
            persist_text_input(
                "Parent Entity Stock Exchange",
                parent_exchange_key,
                help="Enter the stock exchange where the parent entity is listed"
            )
    
    def _render_passive_nfe_section(self, ns: str, instance_id: str) -> None:
        """Render Passive NFE specific fields."""
        st.markdown("**Passive NFE Details**")
        
        # Controlling Person Information (always required for Passive NFE)
        render_controlling_person_section(
            ns, instance_id, 
            self._get_component_registry(),
            "Controlling Person Information (Required for Passive NFE)"
        )
    
    def _render_depository_custodial_insurance_section(self, ns: str, instance_id: str) -> None:
        """Render Depository/Custodial/Insurance Institution specific fields."""
        st.markdown("**Depository/Custodial/Insurance Institution Details**")
        st.markdown(
            """
<div class="callout-info">
  <p>This classification requires no additional fields beyond the basic CRS classification.</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    
    def _render_non_reporting_fi_section(self, ns: str, instance_id: str) -> None:
        """Render Non-Reporting Financial Institution specific fields."""
        st.markdown("**Non-Reporting Financial Institution Details**")
        st.markdown(
            """
<div class="callout-info">
  <p>This classification requires no additional fields beyond the basic CRS classification.</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    
    def _render_other_active_nfe_section(self, ns: str, instance_id: str) -> None:
        """Render Other Active NFE specific fields."""
        st.markdown("**Other Active NFE Details**")
        st.markdown(
            """
<div class="callout-info">
  <p>This classification requires no additional fields beyond the basic CRS classification.</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    
    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        """Validate CRS section data."""
        errors = []
        
        # Get component registry for validation
        component_registry = self._get_component_registry()
        
        # Validate CRS-specific rules
        errors.extend(get_crs_validation_errors(ns, instance_id))
        
        # Validate controlling person sections if present
        crs_class = st.session_state.get(inst_key(ns, instance_id, "crs_classification"), "")
        
        if crs_class == "FI_INVESTMENT_ENTITY":
            investment_entity_type = st.session_state.get(inst_key(ns, instance_id, "investment_entity_type"), "")
            if investment_entity_type == "NON_PARTICIPATING_JURISDICTION":
                errors.extend(validate_controlling_person_section(ns, instance_id, component_registry))
        
        elif crs_class == "PASSIVE_NFE":
            errors.extend(validate_controlling_person_section(ns, instance_id, component_registry))
        
        return errors
    
    def serialize(self, *, ns: str, instance_id: str, **config) -> tuple[Dict[str, Any], List[Any]]:
        """Serialize CRS section data for export."""
        payload = {}
        uploads = []
        
        # Get component registry for serialization
        component_registry = self._get_component_registry()
        
        # Basic CRS classification
        crs_class = st.session_state.get(inst_key(ns, instance_id, "crs_classification"), "")
        if crs_class:
            payload["CRS Classification"] = crs_class
        
        # Investment Entity specific data
        if crs_class == "FI_INVESTMENT_ENTITY":
            investment_entity_type = st.session_state.get(inst_key(ns, instance_id, "investment_entity_type"), "")
            if investment_entity_type:
                payload["Investment Entity Type"] = investment_entity_type
            
            if investment_entity_type == "NON_PARTICIPATING_JURISDICTION":
                # Serialize controlling person data
                cp_payload, cp_uploads = serialize_controlling_person_section(ns, instance_id, component_registry)
                payload.update(cp_payload)
                uploads.extend(cp_uploads)
        
        # Stock Exchange specific data
        elif crs_class == "ACTIVE_NFE_STOCK_EXCHANGE":
            stock_exchange = st.session_state.get(inst_key(ns, instance_id, "stock_exchange_name"), "")
            if stock_exchange:
                payload["Stock Exchange Name"] = stock_exchange
            
            ticker_symbol = st.session_state.get(inst_key(ns, instance_id, "entity_ticker_symbol"), "")
            if ticker_symbol:
                payload["Entity Ticker/Symbol"] = ticker_symbol
            
            related_entity = st.session_state.get(inst_key(ns, instance_id, "related_entity_regularly_traded"), False)
            payload["Related Entity of Regularly Traded Corporation"] = "Yes" if related_entity else "No"
            
            if related_entity:
                parent_name = st.session_state.get(inst_key(ns, instance_id, "parent_entity_name"), "")
                if parent_name:
                    payload["Parent Entity Name"] = parent_name
                
                parent_exchange = st.session_state.get(inst_key(ns, instance_id, "parent_entity_stock_exchange"), "")
                if parent_exchange:
                    payload["Parent Entity Stock Exchange"] = parent_exchange
        
        # Passive NFE specific data
        elif crs_class == "PASSIVE_NFE":
            # Serialize controlling person data
            cp_payload, cp_uploads = serialize_controlling_person_section(ns, instance_id, component_registry)
            payload.update(cp_payload)
            uploads.extend(cp_uploads)
        
        return payload, uploads
    
    def _get_component_registry(self):
        """Get the component registry for accessing other components."""
        # Import here to avoid circular imports
        from app.common_form_sections import get_component_registry
        return get_component_registry()
