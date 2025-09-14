# app/common_form_sections/authorised_representative.py

from __future__ import annotations
import datetime
import re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.utils import inst_key
from app.utils import (
    persist_text_input, persist_selectbox, persist_date_input, persist_file_uploader
)
from app.controlled_lists_enhanced import (
    get_title_options, get_gender_options, get_marital_status_options, get_countries,
    get_dial_code_for_country_label
)

def _digits_only(s: str) -> str:
    """Extract only digits from string."""
    return re.sub(r"\D", "", s or "")

def _luhn_ok(n: str) -> bool:
    """Luhn algorithm check for SA ID validation."""
    n = _digits_only(n)
    total, alt = 0, False
    for d in n[::-1]:
        d = int(d)
        if alt:
            d *= 2
            if d > 9: 
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0

def _valid_sa_id(n: str) -> bool:
    """Validate SA ID Number: 13 digits + Luhn check."""
    n = _digits_only(n)
    return len(n) == 13 and _luhn_ok(n)

def _is_future_date(d: datetime.date | None) -> bool:
    """Check if date is in the future."""
    return bool(d and d > datetime.date.today())

def _is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    email = email.strip()
    if not email:
        return False
    # Basic regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def _phone_ok(dial: str, number: str) -> bool:
    """Validate phone format by dialing code, consistent with PhoneComponent.
    South Africa (+27): 9 digits, no leading zero. International: 6–15 digits.
    """
    dial = (dial or "").strip()
    num_digits = _digits_only(number)
    if dial == "+27":
        return len(num_digits) == 9 and not num_digits.startswith("0")
    return 6 <= len(num_digits) <= 15

class AuthorisedRepresentativeComponent(SectionComponent):
    """
    Component for capturing Authorised Representative details.
    
    The Authorised Representative is the individual completing the form 
    on behalf of the entity.
    
    Config (kwargs):
      - title: str = "Authorised Representative" (section heading)
    """

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Authorised Representative")
        
        st.subheader(title)
        st.caption("The individual completing this form on behalf of the entity.")
        
        # Personal Details Section
        st.markdown("**Personal Details**")
        col1, col2 = st.columns(2)
        
        with col1:
            persist_selectbox("Title", 
                inst_key(ns, instance_id, "title"),
                options=get_title_options(include_empty=True, return_codes=False))
            
            persist_text_input("First Name", 
                inst_key(ns, instance_id, "first_name"))
                
            persist_selectbox("Gender", 
                inst_key(ns, instance_id, "gender"),
                options=get_gender_options(include_empty=True, return_codes=False))
                
            persist_selectbox("Marital Status", 
                inst_key(ns, instance_id, "marital_status"), 
                options=get_marital_status_options(include_empty=True, return_codes=False))
        
        with col2:
            persist_text_input("Last Name", 
                inst_key(ns, instance_id, "last_name"))
                
            persist_date_input("Date of Birth", 
                inst_key(ns, instance_id, "date_of_birth"),
                help="Format: YYYY/MM/DD",
                min_value=datetime.date(1900, 1, 1),  # Reasonable minimum birth year
                max_value=datetime.date.today() - datetime.timedelta(days=365*18))  # Minimum 18 years old
        
        # Identification Section
        st.markdown("**Identification**")
        
        id_type = persist_selectbox("Identification Type",
            inst_key(ns, instance_id, "id_type"),
            options=["", "SA ID Number", "Foreign ID Number", "Foreign Passport Number"])
        
        if id_type == "SA ID Number":
            persist_text_input("SA ID Number", 
                inst_key(ns, instance_id, "sa_id"),
                help="13 digits; Luhn validation applied")
                
        elif id_type == "Foreign ID Number":
            persist_text_input("Foreign ID Number", 
                inst_key(ns, instance_id, "foreign_id"))
                
        elif id_type == "Foreign Passport Number":
            col1, col2 = st.columns(2)
            with col1:
                persist_text_input("Passport Number", 
                    inst_key(ns, instance_id, "passport_number"))
                    
            with col2:
                persist_selectbox("Passport Issue Country",
                    inst_key(ns, instance_id, "passport_country"),
                    options=get_countries(include_empty=True, return_codes=False))
                    
            persist_date_input("Passport Expiry Date",
                inst_key(ns, instance_id, "passport_expiry"),
                min_value=datetime.date.today() + datetime.timedelta(days=1),
                help="Must be a future date")
        
        # Document Upload Section (for Foreign ID and Passport only)
        if id_type in ["Foreign ID Number", "Foreign Passport Number"]:
            st.markdown("**Document Upload**")
            st.info("📎 **Document Upload Guidelines**: Please ensure your total attachment size does not exceed 25MB, otherwise the submission may fail.")
            doc_label = "ID Document" if id_type == "Foreign ID Number" else "Passport Document"
            persist_file_uploader(doc_label,
                inst_key(ns, instance_id, "id_document"))
        
        # Contact Information Section
        st.markdown("**Contact Information**")
        col1, col2 = st.columns(2)
        
        with col1:
            persist_text_input("Email Address", 
                inst_key(ns, instance_id, "email"),
                help="Valid email format required")
                
            citizenship = persist_selectbox("Citizenship", 
                inst_key(ns, instance_id, "citizenship"),
                options=get_countries(include_empty=True, return_codes=False))
        
        with col2:
            # Phone details integrated here (dialing code + number)
            pc1, pc2 = st.columns([1,2])
            with pc1:
                # Auto-fill dialing code based on Citizenship if available (before creating widget)
                phone_code_key = inst_key(ns, instance_id, "phone_code")
                citizenship_value = st.session_state.get(inst_key(ns, instance_id, "citizenship"), "")
                auto_code = get_dial_code_for_country_label(citizenship_value)
                current_code = st.session_state.get(phone_code_key)
                if auto_code and not current_code:
                    # Set only permanent key - persist_widget will handle the temp key
                    st.session_state[phone_code_key] = auto_code
                persist_text_input("Dialing Code", 
                    phone_code_key,
                    help="Auto-filled from Citizenship; edit if needed (e.g., +27)")
            with pc2:
                # Prefer the widget tmp value for label logic if present
                pc_perm_key = inst_key(ns, instance_id, "phone_code")
                pc_tmp_key = f"_{pc_perm_key}"
                current_dial = st.session_state.get(pc_tmp_key) or st.session_state.get(pc_perm_key)
                phone_label = (
                    "Phone Number (must be 9 digits, no leading 0)" if current_dial == "+27"
                    else "Phone Number (digits only)"
                )
                persist_text_input(phone_label, inst_key(ns, instance_id, "phone_number"))
                
            # Get the current residence value first
            residence_key = inst_key(ns, instance_id, "country_of_residence")
            current_residence = st.session_state.get(residence_key, "")
            
            # If dialing code not set from Citizenship, try Country of Residence (before widget creation)
            if not st.session_state.get(phone_code_key) and current_residence:
                auto_code_res = get_dial_code_for_country_label(current_residence)
                if auto_code_res:
                    # Set only permanent key - persist_widget will handle the temp key
                    st.session_state[phone_code_key] = auto_code_res
            
            residence = persist_selectbox("Country of Residence", 
                residence_key,
                options=get_countries(include_empty=True, return_codes=False))
        


    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        # Check if development mode is enabled - if so, skip all validation
        try:
            from app.utils import is_dev_mode
            if is_dev_mode():
                return []  # Return empty list (no errors) when dev mode is enabled
        except ImportError:
            pass  # If utils import fails, continue with normal validation
        
        errs: List[str] = []
        prefix = "[Authorised Representative]"
        
        # Required personal details
        if not (st.session_state.get(inst_key(ns, instance_id, "title")) or "").strip():
            errs.append(f"{prefix} Title is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "first_name")) or "").strip():
            errs.append(f"{prefix} First Name is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "last_name")) or "").strip():
            errs.append(f"{prefix} Last Name is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "gender")) or "").strip():
            errs.append(f"{prefix} Gender is required.")
            
        date_of_birth = st.session_state.get(inst_key(ns, instance_id, "date_of_birth"))
        if not date_of_birth:
            errs.append(f"{prefix} Date of Birth is required.")
        elif date_of_birth >= datetime.date.today() - datetime.timedelta(days=365*18):
            errs.append(f"{prefix} Date of Birth indicates person must be at least 18 years old.")
            
# Marital Status is now optional - removed requirement validation
        
        # Identification validation
        id_type = st.session_state.get(inst_key(ns, instance_id, "id_type"), "")
        if not id_type:
            errs.append(f"{prefix} Identification Type is required.")
        elif id_type == "SA ID Number":
            sa_id = st.session_state.get(inst_key(ns, instance_id, "sa_id"), "")
            if not _valid_sa_id(sa_id):
                errs.append(f"{prefix} SA ID Number is invalid (must be 13 digits with valid Luhn check).")
        elif id_type == "Foreign ID Number":
            foreign_id = st.session_state.get(inst_key(ns, instance_id, "foreign_id"), "")
            if not foreign_id.strip():
                errs.append(f"{prefix} Foreign ID Number is required.")
        elif id_type == "Foreign Passport Number":
            passport_number = st.session_state.get(inst_key(ns, instance_id, "passport_number"), "")
            passport_country = st.session_state.get(inst_key(ns, instance_id, "passport_country"), "")
            passport_expiry = st.session_state.get(inst_key(ns, instance_id, "passport_expiry"))
            
            if not passport_number.strip():
                errs.append(f"{prefix} Passport Number is required.")
            if not passport_country.strip():
                errs.append(f"{prefix} Passport Issue Country is required.")
            if not passport_expiry or not _is_future_date(passport_expiry):
                errs.append(f"{prefix} Passport Expiry Date must be a future date.")
        
        # Document upload validation for Foreign ID and Foreign Passport
        if id_type in ["Foreign ID Number", "Foreign Passport Number"]:
            id_doc = st.session_state.get(inst_key(ns, instance_id, "id_document"))
            if not id_doc:
                doc_type = "ID Document" if id_type == "Foreign ID Number" else "Passport Document"
                errs.append(f"{prefix} {doc_type} upload is required for {id_type}.")
        
        # Contact information validation
        email = st.session_state.get(inst_key(ns, instance_id, "email"), "")
        if not _is_valid_email(email):
            errs.append(f"{prefix} Valid Email Address is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "citizenship")) or "").strip():
            errs.append(f"{prefix} Citizenship is required.")
            
        if not (st.session_state.get(inst_key(ns, instance_id, "country_of_residence")) or "").strip():
            errs.append(f"{prefix} Country of Residence is required.")
            
        # Phone validation (dial code + number)
        dial = st.session_state.get(inst_key(ns, instance_id, "phone_code"), "")
        num = st.session_state.get(inst_key(ns, instance_id, "phone_number"), "")
        if not dial:
            errs.append(f"{prefix} Dialing Code is required.")
        if not num:
            errs.append(f"{prefix} Phone Number is required.")
        if dial and num and not _phone_ok(dial, num):
            errs.append(f"{prefix} Phone Number is invalid for the specified dialing code.")
        
        
        return errs

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        # Collect all authorised representative data
        data = {
            "Title": st.session_state.get(inst_key(ns, instance_id, "title"), ""),
            "First Name": st.session_state.get(inst_key(ns, instance_id, "first_name"), ""),
            "Last Name": st.session_state.get(inst_key(ns, instance_id, "last_name"), ""),
            "Gender": st.session_state.get(inst_key(ns, instance_id, "gender"), ""),
            "Date of Birth": st.session_state.get(inst_key(ns, instance_id, "date_of_birth"), ""),
            "Marital Status": st.session_state.get(inst_key(ns, instance_id, "marital_status"), ""),
            
            "Identification Type": st.session_state.get(inst_key(ns, instance_id, "id_type"), ""),
            "SA ID": st.session_state.get(inst_key(ns, instance_id, "sa_id"), ""),
            "Foreign ID": st.session_state.get(inst_key(ns, instance_id, "foreign_id"), ""),
            "Passport Number": st.session_state.get(inst_key(ns, instance_id, "passport_number"), ""),
            "Passport Country": st.session_state.get(inst_key(ns, instance_id, "passport_country"), ""),
            "Passport Expiry": st.session_state.get(inst_key(ns, instance_id, "passport_expiry"), ""),
            
            "Email": st.session_state.get(inst_key(ns, instance_id, "email"), ""),
            "Citizenship": st.session_state.get(inst_key(ns, instance_id, "citizenship"), ""),
            "Country of Residence": st.session_state.get(inst_key(ns, instance_id, "country_of_residence"), ""),
            "Phone Dialing Code": st.session_state.get(inst_key(ns, instance_id, "phone_code"), ""),
            "Phone Number": st.session_state.get(inst_key(ns, instance_id, "phone_number"), ""),
        }
        
        # Format date of birth if present
        date_of_birth = data["Date of Birth"]
        if isinstance(date_of_birth, datetime.date):
            data["Date of Birth"] = date_of_birth.strftime("%Y/%m/%d")
            
        # Format passport expiry if present
        passport_expiry = data["Passport Expiry"]
        if isinstance(passport_expiry, datetime.date):
            data["Passport Expiry"] = passport_expiry.strftime("%Y/%m/%d")
        
        # Handle file uploads for Foreign ID and Foreign Passport
        uploads = []
        id_type = data["Identification Type"]
        if id_type in ["Foreign ID Number", "Foreign Passport Number"]:
            id_doc = st.session_state.get(inst_key(ns, instance_id, "id_document"))
            if id_doc:
                uploads.append(id_doc)
        
        return data, uploads

    def serialize_with_metadata(self, *, ns: str, instance_id: str, 
                               attachment_collector, 
                               section_title: str, **config) -> Dict[str, Any]:
        """Enhanced serialization with proper attachment naming."""
        
        # Get person details for identifier
        first_name = st.session_state.get(inst_key(ns, instance_id, "first_name"), "")
        last_name = st.session_state.get(inst_key(ns, instance_id, "last_name"), "")
        id_type = st.session_state.get(inst_key(ns, instance_id, "id_type"), "")
        
        # Create identifier using utility function
        from app.attachment_metadata import create_person_identifier, get_document_type_from_id_type
        person_identifier = create_person_identifier(first_name, last_name, "Auth_Rep", 1)
        
        # Get existing payload (reuse existing serialization logic)
        payload, uploads = self.serialize(ns=ns, instance_id=instance_id, **config)
        
        # Add attachments with enhanced metadata for Foreign ID and Foreign Passport
        if id_type in ["Foreign ID Number", "Foreign Passport Number"]:
            id_doc = st.session_state.get(inst_key(ns, instance_id, "id_document"))
            if id_doc:
                doc_type = get_document_type_from_id_type(id_type)
                attachment_collector.add_attachment(
                    file=id_doc,
                    section_title=section_title,
                    document_type=doc_type,
                    person_identifier=person_identifier
                )
        
        return payload


# Register the component
# Component will be registered in __init__.py to avoid circular imports
