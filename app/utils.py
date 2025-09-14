# app/utils.py

import base64
import re
from pathlib import Path
from typing import List
import streamlit as st
import datetime

# Import controlled lists from enhanced centralized module
from app.controlled_lists_enhanced import (
    get_entity_types,
    get_source_of_funds_options,
    get_industry_options,
    get_countries,
    get_member_role_options
)

# Export for backwards compatibility
ENTITY_TYPES = get_entity_types(include_empty=False, return_codes=False)
SOURCE_OF_FUNDS_OPTIONS = get_source_of_funds_options(include_empty=False, return_codes=False)
INDUSTRY_OPTIONS = get_industry_options(include_empty=False, return_codes=False)
COUNTRIES = get_countries(include_empty=False, return_codes=False)
MEMBER_ROLE_OPTIONS = get_member_role_options(include_empty=False, return_codes=False)

def sanitize_ns(label: str) -> str:
    """Sanitize a label to create a valid namespace identifier."""
    return re.sub(r'[^a-z0-9_]', '', label.strip().lower().replace(' ', '_'))

def current_namespace() -> str:
    """Get the current entity type namespace."""
    return sanitize_ns(st.session_state.get("entity_type", ENTITY_TYPES[0]))

def ns_key(ns: str, key: str) -> str:
    """Create a namespaced key for session state."""
    return f"{ns}__{key}"

def inst_key(ns: str, instance_id: str, key: str) -> str:
    """Namespace a key for a specific component instance (e.g., 'directors')."""
    return ns_key(ns, f"{instance_id}__{key}")

def _cleanup_legacy_values():
    """Clean up any legacy session state values that might cause errors."""
    # Clean up any province values that might be set to "Other" which is no longer valid
    try:
        # Get all keys safely
        all_keys = list(st.session_state.keys()) if hasattr(st.session_state, 'keys') else []
        keys_to_check = [k for k in all_keys if k.endswith("__province")]
        for key in keys_to_check:
            if st.session_state.get(key) == "Other":
                st.session_state[key] = ""
    except Exception:
        # If there's any issue with cleanup, just continue
        pass

def initialize_state():
    """Initializes all required session state variables using setdefault."""
    if 'state_initialized' not in st.session_state:
        
        # Calculate favicon path once and store it
        favicon_path = Path(__file__).resolve().parent.parent / "assets" / "logos" / "favicon.svg"
        
        # Define all default values in a dictionary
        defaults = {
            # New entity onboarding system
            "messages": [],
            "accept": False,
            "entity_type": ENTITY_TYPES[0],
            "entity_user_id": "",
            "entity_display_name": "",
            "s1_name": "", "s1_desig": "",
            "s2_name": "", "s2_desig": "",
            # Development mode toggle for testing
            "dev_mode": False,
            "dev_recipient_email": "jpearse@purplegroup.co.za",
            # Favicon path for consistent use across pages
            "favicon_path": str(favicon_path),
            
            # Legacy DDQ fields (kept for backward compatibility during transition)
            "reg_name": "", "trading_name": "", "reg_no": "", "fsp_no": "",
            "aum": 0.0, "phys_addr": "", "bus_overview": "", "inv_phil": "",
            "research": "", "compliance_proc": "", "regulatory_matters": "",
            "final_notes": "",
            "n_auth": 1, "n_dir": 1, "n_ubo": 0, "n_staff": 1, "n_ic": 1,
            # Completion step tracking
            "step_1_complete": False, "step_2_complete": False, "step_3_complete": False,
            "step_4_complete": False, "step_5_complete": False, "step_6_complete": False,
            "step_7_complete": False, "step_8_complete": False,
        }
        
        # Use setdefault to initialize keys without overwriting existing ones
        for key, value in defaults.items():
            st.session_state.setdefault(key, value)
        
        st.session_state.state_initialized = True
    
    # Always run cleanup to handle legacy values
    _cleanup_legacy_values()

def is_dev_mode() -> bool:
    """Check if development mode is enabled."""
    return st.session_state.get("dev_mode", False)

def toggle_dev_mode():
    """Toggle development mode on/off."""
    st.session_state.dev_mode = not st.session_state.get("dev_mode", False)

def persist_widget(widget_func, label: str, state_key: str, **kwargs):
    """A generic helper to make any widget's state survive page switches."""
    tmp_key = f"_{state_key}"  # Temporary key for the widget

    # On the first run, copy the value from the permanent key to the temporary key
    if tmp_key not in st.session_state and state_key in st.session_state:
        st.session_state[tmp_key] = st.session_state[state_key]

    # The callback to copy the widget's value to the permanent key
    def _store_value():
        if tmp_key in st.session_state:
            st.session_state[state_key] = st.session_state[tmp_key]

    # Create the widget with the temporary key and the callback
    widget_func(label, key=tmp_key, on_change=_store_value, **kwargs)

    # Return the value from the permanent key
    return st.session_state.get(state_key)

# Specific helpers for each widget type
def persist_text_input(label: str, state_key: str, **kwargs):
    """Persistent text input widget."""
    return persist_widget(st.text_input, label, state_key, **kwargs)

def persist_text_area(label: str, state_key: str, **kwargs):
    """Persistent text area widget."""
    return persist_widget(st.text_area, label, state_key, **kwargs)

def persist_number_input(label: str, state_key: str, **kwargs):
    """Persistent number input widget."""
    return persist_widget(st.number_input, label, state_key, **kwargs)

def persist_date_input(label: str, state_key: str, **kwargs):
    """Persistent date input widget."""
    return persist_widget(st.date_input, label, state_key, **kwargs)
    
def persist_selectbox(label: str, state_key: str, **kwargs):
    """Persistent selectbox widget."""
    return persist_widget(st.selectbox, label, state_key, **kwargs)

def persist_checkbox(label: str, state_key: str, **kwargs):
    """Persistent checkbox widget."""
    return persist_widget(st.checkbox, label, state_key, **kwargs)

def persist_file_uploader(label: str, state_key: str, **kwargs):
    """Persistent file uploader widget with max file size enforcement.

    Enforces a per-file size limit (default 4 MB). Oversized files are ignored
    and a user-facing error is displayed. For multiple uploads, oversized files
    are filtered out while valid files are retained.
    
    Note: File uploaders use direct session state management to avoid 
    StreamlitValueAssignmentNotAllowedError in cloud environments.
    """
    def _get_max_upload_mb() -> int:
        try:
            # Optional override via secrets: [app] max_upload_mb = 4
            return int(st.secrets.get("app", {}).get("max_upload_mb", 4))
        except Exception:
            return 4

    def _file_size_bytes(uploaded_file) -> int | None:
        """Get file size in bytes safely."""
        if uploaded_file is None:
            return None
        try:
            size_attr = getattr(uploaded_file, "size", None)
            if isinstance(size_attr, int):
                return size_attr
        except Exception:
            pass
        try:
            # Prefer buffer size if available
            buf = uploaded_file.getbuffer()  # type: ignore[attr-defined]
            return getattr(buf, "nbytes", None) or len(buf)
        except Exception:
            try:
                return len(uploaded_file.getvalue())
            except Exception:
                return None

    # File uploaders don't need the persist_widget pattern - use direct approach
    # to avoid session state assignment conflicts in Streamlit Cloud
    
    # Create a unique key for the widget to avoid conflicts
    widget_key = f"_upload_{state_key}"
    
    # Render the file uploader widget directly
    uploaded_files = st.file_uploader(label, key=widget_key, **kwargs)
    
    # Process and validate uploaded files
    max_mb = _get_max_upload_mb()
    limit_bytes = max_mb * 1024 * 1024
    accept_multiple = bool(kwargs.get("accept_multiple_files", False))
    
    if accept_multiple:
        if uploaded_files:
            valid_files = []
            oversized: list[tuple[str, float]] = []
            for f in uploaded_files:
                if f is None:
                    continue
                size_bytes = _file_size_bytes(f)
                if size_bytes is not None and size_bytes > limit_bytes:
                    oversized.append((getattr(f, "name", "<file>"), size_bytes / (1024 * 1024)))
                else:
                    valid_files.append(f)
            
            if oversized:
                names = ", ".join([f"{n} ({sz:.2f} MB)" for n, sz in oversized])
                st.error(f"The following files exceed the {max_mb} MB limit and were ignored: {names}")
            
            # Store valid files in session state
            if valid_files:
                st.session_state[state_key] = valid_files
            elif state_key in st.session_state:
                # Clear the state if no valid files
                st.session_state[state_key] = None
        elif uploaded_files is None and state_key in st.session_state:
            # File uploader returned None - keep existing state
            pass  # Don't modify existing uploads
    else:
        # Single file upload
        if uploaded_files is not None:
            size_bytes = _file_size_bytes(uploaded_files)
            if size_bytes is not None and size_bytes > limit_bytes:
                mb = size_bytes / (1024 * 1024)
                name = getattr(uploaded_files, "name", "<file>")
                st.error(f"File exceeds the {max_mb} MB limit: {name} ({mb:.2f} MB). Please upload a smaller file.")
                # Don't store oversized files
                if state_key in st.session_state:
                    st.session_state[state_key] = None
            else:
                # Store valid file
                st.session_state[state_key] = uploaded_files
        elif uploaded_files is None and state_key not in st.session_state:
            # Initialize state for new uploader
            st.session_state[state_key] = None

    return st.session_state.get(state_key)

def persist_multiselect(label: str, state_key: str, **kwargs):
    """Persistent multiselect widget."""
    return persist_widget(st.multiselect, label, state_key, **kwargs)

def repeat_prefix(idx: int, label: str) -> str:
    """Prefix repeated-section labels with an enumerator (1-based)."""
    return f"**{label} #{idx+1}**"

def text_wrap(text: str, width: int) -> List[str]:
    """Rudimentary word wrap for PDF lines to prevent overflow."""
    words, out, line = str(text).split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return out

def get_completion_progress() -> tuple[int, float]:
    """Calculate completion progress for DDQ steps.
    
    Returns:
        tuple: (completed_steps, progress_percentage)
    """
    completion_steps = [
        "step_1_complete", "step_2_complete", "step_3_complete", "step_4_complete",
        "step_5_complete", "step_6_complete", "step_7_complete", "step_8_complete"
    ]
    
    completed_steps = sum(st.session_state.get(step, False) for step in completion_steps)
    progress_percentage = (completed_steps / 8) * 100
    
    return completed_steps, progress_percentage

def get_favicon_path() -> str:
    """Get the favicon path from session state.
    
    Returns:
        str: Path to the favicon file
    """
    return st.session_state.get("favicon_path", "")

def svg_image_html(path: Path, width: int = 200) -> str:
    """Return an <img> tag with the SVG at the supplied width encoded as base64."""
    try:
        svg_txt = path.read_text(encoding="utf-8")
        encoded = base64.b64encode(svg_txt.encode()).decode()
        return (
            f'<img src="data:image/svg+xml;base64,{encoded}" '
            f'width="{width}" style="margin-bottom:1rem;" />'
        )
    except Exception:
        # If the file cannot be read, return empty string to avoid breaking the UI
        return "" 