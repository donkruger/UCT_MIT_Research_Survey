from __future__ import annotations
import datetime, re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.utils import inst_key
from app.utils import (
    persist_number_input, persist_text_input, persist_selectbox,
    persist_date_input, persist_file_uploader
)
from app.controlled_lists_enhanced import get_member_role_options, get_countries, get_dial_code_for_country_label

def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def _luhn_ok(n: str) -> bool:
    n = _digits_only(n)
    total, alt = 0, False
    for d in n[::-1]:
        d = int(d)
        if alt:
            d *= 2
            if d > 9: d -= 9
        total += d
        alt = not alt
    return total % 10 == 0

def _valid_sa_id(n: str) -> bool:
    n = _digits_only(n)
    return len(n) == 13 and _luhn_ok(n)

def _is_future_date(d: datetime.date | None) -> bool:
    return bool(d and d > datetime.date.today())

class NaturalPersonsComponent(SectionComponent):
    """
    Reusable section for capturing a list of natural persons.
    Config (kwargs):
      - title: str = "Related Natural Persons"
      - role_label: str = "Person"    (used in UI headings)
      - min_count: int = 0            (enforce minimum count)
      - show_uploads: bool = True     (toggle ID/PoA uploads)
      - show_member_roles: bool = False (toggle member role selection)
      - allowed_id_types: list[str] = ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"]
    """

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Related Natural Persons")
        role_label = config.get("role_label", "Person")
        allowed_id_types = config.get("allowed_id_types",
            ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"])

        st.subheader(title)
        count_key = inst_key(ns, instance_id, "count")
        n = persist_number_input(f"Number of {role_label.lower()}s", count_key, min_value=0, step=1)

        for i in range(st.session_state.get(count_key, 0)):
            with st.expander(f"{role_label} #{i+1}", expanded=False):
                
                # Entity Roles - Natural Persons Field Spec implementation
                col1, col2 = st.columns(2)
                with col1:
                    # 1. FirstName (Required)
                    persist_text_input("First Name", inst_key(ns, instance_id, f"first_name_{i}"))
                    
                    # 4. Date of Birth (Required)
                    persist_date_input("Date of Birth", 
                        inst_key(ns, instance_id, f"date_of_birth_{i}"),
                        help="Format: YYYY/MM/DD",
                        max_value=datetime.date.today() - datetime.timedelta(days=1))
                
                with col2:
                    # 2. Surname (Required)
                    persist_text_input("Surname", inst_key(ns, instance_id, f"surname_{i}"))
                    
                    # 6. Country of Residence (Required)
                    persist_selectbox("Country of Residence",
                        inst_key(ns, instance_id, f"residence_country_{i}"),
                        options=get_countries(include_empty=True, return_codes=False))
                
                # 3. UserID (Optional - only if person has platform account)
                persist_text_input("User ID (if applicable)", 
                    inst_key(ns, instance_id, f"user_id_{i}"),
                    help="Internal platform identifier if person has an account")
                
                # Member role selection (if enabled)
                if config.get("show_member_roles", False):
                    persist_selectbox("Member Role",
                        inst_key(ns, instance_id, f"member_role_{i}"),
                        options=get_member_role_options(include_empty=True, return_codes=False))

                id_type = persist_selectbox("Identification Type",
                    inst_key(ns, instance_id, f"id_type_{i}"),
                    options=[""] + allowed_id_types)

                if id_type == "SA ID Number":
                    persist_text_input("SA ID Number", inst_key(ns, instance_id, f"sa_id_{i}"),
                                       help="13 digits; Luhn check applies.")
                elif id_type == "Foreign ID Number":
                    persist_text_input("Foreign ID Number", inst_key(ns, instance_id, f"foreign_id_{i}"))
                elif id_type == "Foreign Passport Number":
                    persist_text_input("Passport Number", inst_key(ns, instance_id, f"passport_no_{i}"))
                    persist_selectbox("Passport Issue Country",
                        inst_key(ns, instance_id, f"passport_country_{i}"),
                        options=get_countries())
                    persist_date_input("Passport Expiry (YYYY/MM/DD)",
                        inst_key(ns, instance_id, f"passport_expiry_{i}"),
                        min_value=datetime.date.today() + datetime.timedelta(days=1))

                persist_text_input("Email", inst_key(ns, instance_id, f"email_{i}"))
                # Auto-fill dialing code based on residence country where possible
                dial_key = inst_key(ns, instance_id, f"tel_code_{i}")
                residence_country = st.session_state.get(inst_key(ns, instance_id, f"residence_country_{i}"), "")
                auto_dial = get_dial_code_for_country_label(residence_country)
                if auto_dial and not st.session_state.get(dial_key):
                    # Set only permanent key - persist_widget will handle the temp key
                    st.session_state[dial_key] = auto_dial
                dc, pn = st.columns([1,2])
                with dc:
                    persist_text_input("Dialing Code", dial_key, help="Auto-filled from Country of Residence")
                with pn:
                    persist_text_input("Telephone", inst_key(ns, instance_id, f"tel_{i}"))
                
                # Role-specific additional fields per Entity Roles Rules Specification
                self._render_role_specific_fields(ns, instance_id, i, config)

                if config.get("show_uploads", True):
                    persist_file_uploader("ID / Passport Document",
                        inst_key(ns, instance_id, f"id_doc_{i}"))
                    persist_file_uploader("Proof of Address",
                        inst_key(ns, instance_id, f"poa_doc_{i}"))

    def _render_role_specific_fields(self, ns: str, instance_id: str, i: int, config: dict):
        """Render additional fields based on the role per Entity Roles Rules Specification."""
        role_label = config.get("role_label", "Person").lower()
        
        # Executive Control for Company Directors, CC Members, and Partners
        if role_label in ["director", "member", "partner"]:
            persist_selectbox("Executive Control",
                inst_key(ns, instance_id, f"executive_control_{i}"),
                options=["", "Yes", "No"],
                help="Does this person exercise executive control?")
        
        # Percentage fields for different roles
        if role_label == "member":  # CC Members
            persist_number_input("Member Interest Percentage (%)",
                inst_key(ns, instance_id, f"member_interest_{i}"),
                min_value=0.0, max_value=100.0, step=0.01,
                help="Ownership percentage in the CC (0-100%)")
        elif role_label == "partner":  # Partnership Partners
            persist_number_input("Partner Interest (%)",
                inst_key(ns, instance_id, f"partner_interest_{i}"),
                min_value=0.0, max_value=100.0, step=0.01,
                help="Ownership percentage in the Partnership (0-100%)")
        elif role_label in ["shareholder", "owner"]:  # Company Shareholders/Beneficial Owners
            persist_number_input("Percentage Shareholding (%)",
                inst_key(ns, instance_id, f"shareholding_{i}"),
                min_value=0.0, max_value=100.0, step=0.01,
                help="Ownership percentage in the Company (0-100%)")

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        errs: List[str] = []
        role_label = config.get("role_label", "Person")
        min_count = int(config.get("min_count", 0))
        allowed_id_types = config.get("allowed_id_types",
            ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"])

        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)
        if n < min_count:
            errs.append(f"[{role_label}s] At least {min_count} entr{'y' if min_count==1 else 'ies'} required.")

        for i in range(n):
            prefix = f"[{role_label} #{i+1}]"
            
            # Required fields per Natural Persons Field Spec
            first_name = st.session_state.get(inst_key(ns, instance_id, f"first_name_{i}"), "").strip()
            surname = st.session_state.get(inst_key(ns, instance_id, f"surname_{i}"), "").strip()
            date_of_birth = st.session_state.get(inst_key(ns, instance_id, f"date_of_birth_{i}"), None)
            residence_country = st.session_state.get(inst_key(ns, instance_id, f"residence_country_{i}"), "").strip()
            
            if not first_name:
                errs.append(f"{prefix} First Name is required.")
            if not surname:
                errs.append(f"{prefix} Surname is required.")
            if not date_of_birth:
                errs.append(f"{prefix} Date of Birth is required.")
            elif date_of_birth >= datetime.date.today():
                errs.append(f"{prefix} Date of Birth must be a past date.")
            if not residence_country:
                errs.append(f"{prefix} Country of Residence is required.")

            idt = st.session_state.get(inst_key(ns, instance_id, f"id_type_{i}"), "")
            if idt not in [""] + allowed_id_types:
                errs.append(f"{prefix} Invalid ID Type.")
            if not idt:
                errs.append(f"{prefix} Identification Type is required.")
            if idt == "SA ID Number":
                val = st.session_state.get(inst_key(ns, instance_id, f"sa_id_{i}"), "")
                if not _valid_sa_id(val):
                    errs.append(f"{prefix} SA ID Number is invalid.")
            elif idt == "Foreign ID Number":
                if not (st.session_state.get(inst_key(ns, instance_id, f"foreign_id_{i}")) or "").strip():
                    errs.append(f"{prefix} Foreign ID Number is required.")
            elif idt == "Foreign Passport Number":
                if not (st.session_state.get(inst_key(ns, instance_id, f"passport_no_{i}")) or "").strip():
                    errs.append(f"{prefix} Passport Number is required.")
                if not (st.session_state.get(inst_key(ns, instance_id, f"passport_country_{i}")) or "").strip():
                    errs.append(f"{prefix} Passport Issue Country is required.")
                exp = st.session_state.get(inst_key(ns, instance_id, f"passport_expiry_{i}"))
                if not (exp and _is_future_date(exp)):
                    errs.append(f"{prefix} Passport Expiry must be a future date.")
            
            # Member role validation (if enabled)
            if config.get("show_member_roles", False):
                member_role = st.session_state.get(inst_key(ns, instance_id, f"member_role_{i}"), "")
                if not member_role or member_role.strip() == "":
                    errs.append(f"{prefix} Member Role is required.")

        return errs

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        people: List[Dict[str, Any]] = []
        uploads: List[Any] = []
        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)

        for i in range(n):
            exp = st.session_state.get(inst_key(ns, instance_id, f"passport_expiry_{i}"))
            dob = st.session_state.get(inst_key(ns, instance_id, f"date_of_birth_{i}"))
            
            person_data = {
                # Natural Persons Field Spec core fields
                "First Name": st.session_state.get(inst_key(ns, instance_id, f"first_name_{i}"), ""),
                "Surname": st.session_state.get(inst_key(ns, instance_id, f"surname_{i}"), ""),
                "User ID": st.session_state.get(inst_key(ns, instance_id, f"user_id_{i}"), ""),
                "Date of Birth": dob.strftime("%Y/%m/%d") if dob else "",
                "Country of Residence": st.session_state.get(inst_key(ns, instance_id, f"residence_country_{i}"), ""),
                
                # Identification fields
                "ID Type": st.session_state.get(inst_key(ns, instance_id, f"id_type_{i}"), ""),
                "SA ID": st.session_state.get(inst_key(ns, instance_id, f"sa_id_{i}"), ""),
                "Foreign ID": st.session_state.get(inst_key(ns, instance_id, f"foreign_id_{i}"), ""),
                "Passport No": st.session_state.get(inst_key(ns, instance_id, f"passport_no_{i}"), ""),
                "Passport Country": st.session_state.get(inst_key(ns, instance_id, f"passport_country_{i}"), ""),
                "Passport Expiry": exp.strftime("%Y/%m/%d") if exp else "",
                
                # Contact fields
                "Email": st.session_state.get(inst_key(ns, instance_id, f"email_{i}"), ""),
                "Telephone": st.session_state.get(inst_key(ns, instance_id, f"tel_{i}"), ""),
                
                # Upload status
                "ID Doc Uploaded": bool(st.session_state.get(inst_key(ns, instance_id, f"id_doc_{i}"))),
                "PoA Uploaded": bool(st.session_state.get(inst_key(ns, instance_id, f"poa_doc_{i}"))),
            }
            
            # Add member role if enabled
            if config.get("show_member_roles", False):
                person_data["Member Role"] = st.session_state.get(inst_key(ns, instance_id, f"member_role_{i}"), "")
            
            # Add role-specific fields per Entity Roles Rules Specification
            role_label = config.get("role_label", "Person").lower()
            if role_label in ["director", "member", "partner"]:
                person_data["Executive Control"] = st.session_state.get(inst_key(ns, instance_id, f"executive_control_{i}"), "")
            
            if role_label == "member":
                person_data["Member Interest Percentage"] = st.session_state.get(inst_key(ns, instance_id, f"member_interest_{i}"), 0.0)
            elif role_label == "partner":
                person_data["Partner Interest"] = st.session_state.get(inst_key(ns, instance_id, f"partner_interest_{i}"), 0.0)
            elif role_label in ["shareholder", "owner"]:
                person_data["Percentage Shareholding"] = st.session_state.get(inst_key(ns, instance_id, f"shareholding_{i}"), 0.0)
            
            people.append(person_data)
            if config.get("show_uploads", True):
                uploads.extend([
                    st.session_state.get(inst_key(ns, instance_id, f"id_doc_{i}")),
                    st.session_state.get(inst_key(ns, instance_id, f"poa_doc_{i}")),
                ])

        payload = {"Count": n, "Records": people}
        return payload, uploads

# Component will be registered in __init__.py to avoid circular imports
