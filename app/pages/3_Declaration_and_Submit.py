"""
Review and submission page for the Research Survey Application with premium UI/UX.
"""

import streamlit as st
import sys
from pathlib import Path

# --- PAGE CONFIG ---
favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.svg"
st.set_page_config(
    page_title="Review & Submit - Research Survey",
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.sidebar import render_sidebar
from app.components.submission import handle_submission
from app.styling import get_all_styles
from app.utils import initialize_state, persist_checkbox, persist_text_input, current_namespace
from app.forms.specs import SPECS
from app.forms.engine import serialize_answers, validate

# Initialize and apply styling
initialize_state()
st.session_state.current_page = "submit"  # Set current page for progress tracking
st.markdown(get_all_styles(), unsafe_allow_html=True)
render_sidebar()

# Hero section for review page
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    border-radius: 24px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 40px rgba(30, 64, 175, 0.2);
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute;
        top: -30%;
        right: -5%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    "></div>
    <h1 style="
        color: white;
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.02em;
        position: relative;
    ">Review & Submit</h1>
    <p style="
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.125rem;
        margin: 0;
        position: relative;
    ">
        Please review your responses and submit your survey
    </p>
</div>
""", unsafe_allow_html=True)

# Development Mode Indicator with modern styling
try:
    from app.utils import is_dev_mode
    if is_dev_mode():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.1);
        ">
            <div style="display: flex; align-items: center;">
                <div style="
                    background: #f59e0b;
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 1rem;
                    font-weight: bold;
                ">⚡</div>
                <div>
                    <h4 style="margin: 0 0 0.25rem 0; color: #92400e;">Development Mode Active</h4>
                    <p style="margin: 0; color: #78350f; font-size: 0.875rem;">
                        Form validation is disabled for testing purposes
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
except ImportError:
    pass

# Check if a survey has been selected
if 'survey_type' not in st.session_state or not st.session_state.survey_type:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    ">
        <p style="color: #7f1d1d; margin: 0 0 1rem 0;">
            Please complete the survey questions before proceeding to review.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link('main.py', label='← Return to Survey Questions')
    st.stop()

# Get current survey information
survey_type = st.session_state.get('survey_type', '')
survey_display_name = st.session_state.get('survey_display_name', 'Survey')

# Survey information cards
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e9ff 100%);
        border-radius: 16px;
        padding: 1.25rem;
        border: 1px solid #c7d5ff;
        height: 80px;
    ">
        <p style="
            color: #6b7280;
            font-size: 0.75rem;
            margin: 0 0 0.5rem 0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        ">Survey Type</p>
        <p style="
            color: #1f2937;
            font-size: 1.125rem;
            font-weight: 600;
            margin: 0;
        ">{survey_display_name}</p>
    </div>
    """, unsafe_allow_html=True)

# Optional reference
survey_ref = st.session_state.get('survey_reference', '')
with col2:
    if survey_ref:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            border-radius: 16px;
            padding: 1.25rem;
            border: 1px solid #86efac;
            height: 80px;
        ">
            <p style="
                color: #6b7280;
                font-size: 0.75rem;
                margin: 0 0 0.5rem 0;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">Reference</p>
            <p style="
                color: #1f2937;
                font-size: 1.125rem;
                font-weight: 600;
                margin: 0;
            ">{survey_ref}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fafbfc 0%, #f4f6f8 100%);
            border-radius: 16px;
            padding: 1.25rem;
            border: 1px solid #e9ecef;
            height: 80px;
        ">
            <p style="
                color: #9ca3af;
                font-size: 0.75rem;
                margin: 0 0 0.5rem 0;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">Reference</p>
            <p style="
                color: #9ca3af;
                font-size: 1rem;
                margin: 0;
            ">Not provided</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Declaration section with modern card design
st.markdown("""
<div style="
    background: white;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    border: 1px solid #e0e9ff;
    margin-bottom: 2rem;
">
    <h3 style="
        color: #1f2937;
        font-size: 1.5rem;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
    ">
        <span style="
            background: linear-gradient(135deg, #4a69ff 0%, #8b5cf6 100%);
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-size: 1.25rem;
        ">✓</span>
        Declaration
    </h3>
    <p style="
        color: #6b7280;
        line-height: 1.6;
        margin: 0 0 1.5rem 0;
    ">
        Please review your responses and confirm that the information provided is accurate.
    </p>
</div>
""", unsafe_allow_html=True)

# Move the checkbox inside the card visually
persist_checkbox(
    "I confirm that all information provided in this survey is accurate and complete to the best of my knowledge.",
    "accept"
)

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Spacer before submission section
st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

# Final submission section with call-to-action
def reconstruct_payload():
    """Reconstruct the survey payload from session state."""
    ns = current_namespace()
    spec = SPECS.get(ns)
    
    if not spec:
        if not SPECS:
            st.error("No surveys are configured. Please add survey specifications.")
            st.stop()
        else:
            st.error(f"Survey type '{ns}' is not configured.")
            st.stop()
    
    # Check if development mode is active
    try:
        from app.utils import is_dev_mode
        skip_validation = is_dev_mode()
    except ImportError:
        skip_validation = False
    
    # Formal validation pass (component + required fields)
    if not skip_validation:
        errors = validate(spec, ns)
        if errors:
            st.markdown("""
            <div style="
                background: #fee2e2;
                border: 2px solid #ef4444;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            ">
                <h4 style="color: #7f1d1d; margin: 0 0 1rem 0;">
                    Please resolve the following issues:
                </h4>
            </div>
            """, unsafe_allow_html=True)
            for e in errors:
                st.markdown(f"• {e}")
            st.stop()
    
    # Serialize survey answers
    answers, uploads = serialize_answers(spec, ns)
    
    # Attach metadata
    answers["Survey Type"] = survey_display_name
    
    # Add declaration and consent information
    answers["Declaration"] = {
        "Declaration Accepted": st.session_state.get("accept", False),
        "Informed Consent Signed By": st.session_state.get("consent_name", ""),
    }
    
    # Add feedback if available
    if 'feedback_data' in st.session_state:
        answers["Feedback"] = st.session_state['feedback_data']
    
    return answers, uploads

# Submit button with modern design
st.markdown("""
<div style="
    background: linear-gradient(135deg, #4a69ff 0%, #8b5cf6 100%);
    border-radius: 24px;
    padding: 3rem;
    text-align: center;
    box-shadow: 0 10px 40px rgba(74, 105, 255, 0.2);
    margin: 2rem 0;
">
    <h3 style="
        color: white;
        font-size: 1.75rem;
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    ">Ready to Submit?</h3>
    <p style="
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin: 0 0 2rem 0;
    ">
        Your survey responses will be securely transmitted for analysis
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Custom styled button
    submit_button = st.button(
        "Submit Survey →",
        use_container_width=True,
        type="primary",
        key="submit_survey"
    )
    
    if submit_button:
        # Check declaration
        if not st.session_state.get("accept", False):
            st.markdown("""
            <div style="
                background: #fee2e2;
                border: 2px solid #ef4444;
                border-radius: 12px;
                padding: 1rem;
                margin-top: 1rem;
                text-align: center;
            ">
                <p style="color: #7f1d1d; margin: 0;">
                    Please accept the declaration before submitting.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        # Reconstruct and submit with progress indicator
        with st.spinner("Processing your submission..."):
            answers_data, uploaded_files_data = reconstruct_payload()
            handle_submission(answers_data, uploaded_files_data)