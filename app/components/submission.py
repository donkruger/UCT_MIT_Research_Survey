"""
Submission handling component for the Research Survey Application with premium UI/UX.

This module handles the final submission process including PDF generation,
email sending, and providing downloads with beautiful visual feedback.
"""

import datetime
import json
from typing import Dict, List, Any, Optional
import streamlit as st
from app.pdf_generator import make_pdf
from app.email_sender import send_submission_email

def handle_submission(answers: Dict[str, Any], uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]]):
    """
    Handles the survey submission with enhanced UI/UX experience.
    
    Args:
        answers: Complete survey response data
        uploaded_files: List of any uploaded files
    """
    
    # Validate declaration acceptance
    if not st.session_state.get("accept"):
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            border: 2px solid #ef4444;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            text-align: center;
            animation: shake 0.5s;
        ">
            <style>
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                20%, 40%, 60%, 80% { transform: translateX(5px); }
            }
            </style>
            <p style="color: #7f1d1d; margin: 0; font-weight: 500;">
                Please accept the declaration before submitting.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Debug information for development mode
    try:
        from app.utils import is_dev_mode
        if is_dev_mode():
            with st.expander("Development Mode Debug Info"):
                st.json({
                    "survey_type": answers.get("Survey Type", "Unknown"),
                    "answers_keys": list(answers.keys()) if isinstance(answers, dict) else "N/A",
                    "uploaded_files_count": len([f for f in uploaded_files if f is not None])
                })
    except ImportError:
        pass

    # Processing animation with progress
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Extract survey information
    survey_name = st.session_state.get("survey_display_name", "Survey")
    dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_survey_name = survey_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    
    # Create filename
    filename = f"{safe_survey_name}__{dt}.csv"
    pdf_name = f"Survey_{safe_survey_name}_{dt}.pdf"

    # Processing steps with visual feedback
    steps = [
        ("Validating responses", 0.2),
        ("Generating PDF document", 0.4),
        ("Preparing email", 0.6),
        ("Sending submission", 0.8),
        ("Finalizing", 1.0)
    ]
    
    for step_name, progress_value in steps:
        progress_placeholder.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f0f4ff 0%, #e0e9ff 100%);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #4b5563; font-weight: 500;">{step_name}...</span>
                <span style="color: #6b7280;">{int(progress_value * 100)}%</span>
            </div>
            <div style="
                background: rgba(74, 105, 255, 0.1);
                border-radius: 8px;
                height: 8px;
                overflow: hidden;
            ">
                <div style="
                    background: linear-gradient(90deg, #4a69ff 0%, #8b5cf6 100%);
                    height: 100%;
                    width: {progress_value * 100}%;
                    border-radius: 8px;
                    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 2px 8px rgba(74, 105, 255, 0.3);
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Execute actual tasks
        if progress_value == 0.4:  # PDF generation
            try:
                pdf_bytes = make_pdf(answers)
            except Exception as e:
                pdf_bytes = None
                status_placeholder.error(f"PDF generation encountered an issue: {e}")
        
        elif progress_value == 0.8:  # Email sending
            try:
                feedback_data = st.session_state.get('feedback_data')
                send_submission_email(answers, uploaded_files, feedback_data)
                if 'feedback_data' in st.session_state:
                    del st.session_state['feedback_data']
            except Exception as e:
                status_placeholder.warning(f"Email sending encountered an issue: {e}")
                status_placeholder.info("You can still download your submission below.")
    
    # Clear progress indicators
    progress_placeholder.empty()
    status_placeholder.empty()
    
    # Generate CSV
    csv_string = None
    try:
        # Check if this is an investment research survey
        survey_type = st.session_state.get("survey_type", "")
        if survey_type == "investment_research":
            from app.csv_generator import make_investment_research_csv
            csv_string = make_investment_research_csv(answers)
        else:
            from app.csv_generator import make_csv
            csv_string = make_csv(answers)
    except Exception:
        pass

    # Success animation and message
    st.markdown("""
    <style>
    @keyframes successPulse {
        0% { transform: scale(0.95); opacity: 0; }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes checkmark {
        0% { stroke-dashoffset: 50; }
        100% { stroke-dashoffset: 0; }
    }
    </style>
    
    <div style="
        background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 20px 40px rgba(16, 185, 129, 0.2);
        animation: successPulse 0.6s ease-out;
    ">
        <div style="
            width: 80px;
            height: 80px;
            margin: 0 auto 1.5rem;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        ">
            <svg width="48" height="48" viewBox="0 0 48 48" style="animation: checkmark 0.8s ease-out 0.3s forwards;">
                <path d="M14 24 L20 30 L34 16" stroke="#10b981" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="50" stroke-dashoffset="50"/>
            </svg>
        </div>
        <h2 style="
            color: white;
            font-size: 2rem;
            margin: 0 0 0.5rem 0;
            font-weight: 700;
        ">Submission Complete!</h2>
        <p style="
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.125rem;
            margin: 0;
        ">Your research survey has been successfully submitted</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Submission summary cards
    st.markdown("<h3 style='margin: 2rem 0 1rem;'>Submission Details</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        submission_time = datetime.datetime.now().strftime("%H:%M")
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.25rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e9ff;
            text-align: center;
        ">
            <div style="
                background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
                width: 40px;
                height: 40px;
                border-radius: 10px;
                margin: 0 auto 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <span style="color: white; font-size: 1.25rem;">⏰</span>
            </div>
            <p style="color: #6b7280; font-size: 0.75rem; margin: 0 0 0.25rem;">Time</p>
            <p style="color: #1f2937; font-weight: 600; margin: 0;">{submission_time}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        submission_date = datetime.datetime.now().strftime("%d %b")
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.25rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e9ff;
            text-align: center;
        ">
            <div style="
                background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
                width: 40px;
                height: 40px;
                border-radius: 10px;
                margin: 0 auto 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <span style="color: white; font-size: 1.25rem;">📅</span>
            </div>
            <p style="color: #6b7280; font-size: 0.75rem; margin: 0 0 0.25rem;">Date</p>
            <p style="color: #1f2937; font-weight: 600; margin: 0;">{submission_date}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        response_count = len([k for k in answers.keys() if k not in ["Survey Type", "Declaration"]])
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.25rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e9ff;
            text-align: center;
        ">
            <div style="
                background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
                width: 40px;
                height: 40px;
                border-radius: 10px;
                margin: 0 auto 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <span style="color: white; font-size: 1.25rem;">✓</span>
            </div>
            <p style="color: #6b7280; font-size: 0.75rem; margin: 0 0 0.25rem;">Responses</p>
            <p style="color: #1f2937; font-weight: 600; margin: 0;">{response_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Download section with enhanced styling
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #fafbfc 0%, #f4f6f8 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #e9ecef;
    ">
        <h3 style="
            color: #1f2937;
            margin: 0 0 1.5rem 0;
            display: flex;
            align-items: center;
        ">
            <span style="
                background: linear-gradient(135deg, #4a69ff 0%, #8b5cf6 100%);
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 0.75rem;
            ">💾</span>
            Download Your Submission
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Download buttons with better layout
    col1, col2 = st.columns(2)
    
    with col1:
        if pdf_bytes:
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=pdf_name,
                mime="application/pdf",
                use_container_width=True
            )

    with col2:
        if csv_string:
            csv_name = pdf_name.replace('.pdf', '.csv')
            st.download_button(
                label="📊 Download CSV Data",
                data=csv_string,
                file_name=csv_name,
                mime="text/csv",
                use_container_width=True
            )
    
    # Uploaded files section with cards
    valid_uploads = [f for f in uploaded_files if f is not None]
    if valid_uploads:
        st.markdown("<h4 style='margin: 2rem 0 1rem;'>Uploaded Files</h4>", unsafe_allow_html=True)
        cols = st.columns(min(3, len(valid_uploads)))
        for i, f in enumerate(valid_uploads):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border: 1px solid #e0e9ff;
                    text-align: center;
                ">
                    <p style="
                        color: #4b5563;
                        font-size: 0.875rem;
                        margin: 0 0 0.5rem;
                        font-weight: 500;
                    ">{f.name[:20]}...</p>
                </div>
                """, unsafe_allow_html=True)
                st.download_button(
                    "Download", 
                    f.getvalue(), 
                    file_name=f.name, 
                    mime=f.type,
                    use_container_width=True
                )
    
    # Raw data (collapsed, modernized)
    with st.expander("📊 View Raw Submission Data"):
        st.json(json.loads(json.dumps(answers, default=str)), expanded=False)
    
    # Next steps with attractive info box
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #86efac;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
    ">
        <h3 style="
            color: #166534;
            margin: 0 0 1rem 0;
            display: flex;
            align-items: center;
        ">
            <span style="
                background: #10b981;
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 0.75rem;
            ">✓</span>
            What Happens Next?
        </h3>
        <ul style="
            color: #166534;
            line-height: 1.75;
            margin: 0;
            padding-left: 1.25rem;
        ">
            <li>Your response has been securely transmitted to our research team</li>
            <li>Your data will be analyzed as part of our research study</li>
            <li>All responses remain confidential and anonymous</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Submit another survey button with modern styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Submit Another Survey →", use_container_width=True):
            # Clear relevant session state
            for key in list(st.session_state.keys()):
                if key.startswith(st.session_state.get("survey_type", "")) and "__" in key:
                    del st.session_state[key]
            # Clear submission-specific data
            st.session_state.accept = False
            # Navigate to main page
            st.switch_page("main.py")