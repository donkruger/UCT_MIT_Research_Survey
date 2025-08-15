from __future__ import annotations
import re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.common_form_sections import register_component
from app.utils import inst_key
from app.utils import persist_text_input, persist_selectbox

from app.controlled_lists import get_countries

SA_PROVINCES = ["", "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal",
                "Limpopo", "Mpumalanga", "North West", "Northern Cape", "Western Cape"]

# For non-SA addresses, we'll use a simple text input instead of a selectbox

def _postal_ok(code: str, country: str) -> bool:
    if (country or "").strip() == "South Africa":
        return bool(re.fullmatch(r"\d{4}", code or ""))
    return bool(code and len(code) <= 10)  # permissive for non-SA

class AddressComponent(SectionComponent):
    """Reusable address section."""

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Physical Address")
        st.subheader(title)
        
        col1, col2 = st.columns(2)
        with col1:
            persist_text_input("Unit Number (optional)", inst_key(ns, instance_id, "unit_no"))
            persist_text_input("Street Number", inst_key(ns, instance_id, "street_no"))
            persist_text_input("Suburb", inst_key(ns, instance_id, "suburb"))
            persist_selectbox("Country", inst_key(ns, instance_id, "country"), options=get_countries())
        with col2:
            persist_text_input("Complex Name (optional)", inst_key(ns, instance_id, "complex"))
            persist_text_input("Street Name", inst_key(ns, instance_id, "street_name"))
            persist_text_input("City", inst_key(ns, instance_id, "city"))
            # Province field - dropdown for SA, text input for other countries  
            selected_country = st.session_state.get(inst_key(ns, instance_id, "country"), "")
            if selected_country == "South Africa":
                persist_selectbox("Province", inst_key(ns, instance_id, "province"), options=SA_PROVINCES)
            else:
                persist_text_input("Province/State/Region", inst_key(ns, instance_id, "province"))
        
        # Postal Code
        pc_label = "Postal Code (must be 4 digits)" if st.session_state.get(inst_key(ns, instance_id, "country")) == "South Africa" else "Postal Code"
        persist_text_input(pc_label, inst_key(ns, instance_id, "code"))

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        errs: List[str] = []
        def req(k, label): 
            if not (st.session_state.get(inst_key(ns, instance_id, k)) or "").strip():
                errs.append(f"[Address] {label} is required.")
        
        req("street_no", "Street Number")
        req("street_name", "Street Name")
        req("suburb", "Suburb")
        req("city", "City")
        
        country = (st.session_state.get(inst_key(ns, instance_id, "country")) or "").strip()
        if country == "South Africa" and not (st.session_state.get(inst_key(ns, instance_id, "province")) or "").strip():
            errs.append("[Address] Province is required for South Africa.")
        
        code = st.session_state.get(inst_key(ns, instance_id, "code"), "")
        if not _postal_ok(code, country):
            errs.append("[Address] Postal Code is invalid.")
        
        return errs

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        payload = {
            "Unit Number": st.session_state.get(inst_key(ns, instance_id, "unit_no"), ""),
            "Complex Name": st.session_state.get(inst_key(ns, instance_id, "complex"), ""),
            "Street Number": st.session_state.get(inst_key(ns, instance_id, "street_no"), ""),
            "Street Name": st.session_state.get(inst_key(ns, instance_id, "street_name"), ""),
            "Suburb": st.session_state.get(inst_key(ns, instance_id, "suburb"), ""),
            "City": st.session_state.get(inst_key(ns, instance_id, "city"), ""),
            "Province": st.session_state.get(inst_key(ns, instance_id, "province"), ""),
            "Country": st.session_state.get(inst_key(ns, instance_id, "country"), ""),
            "Postal Code": st.session_state.get(inst_key(ns, instance_id, "code"), ""),
        }
        return payload, []

# Register
register_component("address", AddressComponent())
