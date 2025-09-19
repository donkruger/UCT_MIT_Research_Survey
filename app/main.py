"""
Main entry point for the Investment Decision-Making Research Survey Application.

This module provides the main survey form page with modern UI/UX design.
"""

from __future__ import annotations
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.styling import get_all_styles
from app.components.sidebar import render_sidebar
from app.utils import initialize_state, persist_text_input, current_namespace, ns_key
from app.forms.engine import render_form
from app.forms.specs import SPECS

def render_progress_bar():
    """Render a beautiful progress indicator with 3-step process."""
    # Calculate progress based on filled fields within the questionnaire
    total_fields = 23  # Total questions in the survey
    filled_fields = sum(1 for key in st.session_state.keys() if "__" in key and st.session_state[key])
    questionnaire_progress = min(filled_fields / total_fields, 1.0)
    
    # Overall progress considering the 3-step process
    consent_given = st.session_state.get("consent_given", False)
    if not consent_given:
        overall_progress = 0.0
    else:
        # Consent is complete (33%), questionnaire progress contributes to next 33%
        overall_progress = 0.33 + (questionnaire_progress * 0.34)  # 33% + up to 34% = 67% max before submit
    
    progress_html = f"""
    <div style="
        background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
        border: 1px solid #0ea5e9;
    ">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-size: 0.875rem; color: #1e40af; font-weight: 600;">
                Research Study Progress
            </span>
            <span style="font-size: 0.875rem; color: #3b82f6;">
                Step 2 of 3 • Questionnaire {int(questionnaire_progress * 100)}% Complete
            </span>
        </div>
        <div style="
            background: rgba(30, 64, 175, 0.1);
            border-radius: 8px;
            height: 8px;
            overflow: hidden;
            position: relative;
        ">
            <div style="
                background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
                height: 100%;
                width: {overall_progress * 100}%;
                border-radius: 8px;
                transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 4px rgba(30, 64, 175, 0.3);
            "></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.75rem; color: #64748b;">
            <span>✓ Consent Given</span>
            <span>{'✓ Questionnaire Complete' if questionnaire_progress >= 1.0 else '◦ Questionnaire In Progress'}</span>
            <span>◦ Ready to Submit</span>
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def render_hero_section():
    """Render an impressive hero section."""
    hero_html = """
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 24px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(30, 64, 175, 0.2);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50%;
            right: -10%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            border-radius: 50%;
        "></div>
        <div style="
            position: absolute;
            bottom: -30%;
            left: -5%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
            border-radius: 50%;
        "></div>
        <div style="
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            color: white;
        ">UCT Research Study</div>
        <h1 style="
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0 0 1rem 0;
            letter-spacing: -0.02em;
            position: relative;
        ">AI Investment Advisory Research</h1>
        <p style="
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.125rem;
            line-height: 1.75;
            margin: 0;
            position: relative;
        ">
            University of Cape Town • Department of Information Systems<br>
            Evaluating user experiences with multi-agent AI investment advisory systems
        </p>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

def render_info_cards():
    """Render information cards with modern design."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #dbeafe;
            height: 150px;
            transition: all 0.3s ease;
        ">
            <div style="
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            ">
                <span style="color: white; font-size: 1.5rem;">🤖</span>
            </div>
            <h3 style="font-size: 1rem; color: #374151; margin: 0 0 0.25rem 0;">Multi-Agent AI System</h3>
            <p style="font-size: 0.875rem; color: #6b7280; margin: 0;">Evaluate AI-driven investment advice</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #dbeafe;
            height: 150px;
        ">
            <div style="
                background: linear-gradient(135deg, #059669 0%, #10b981 100%);
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            ">
                <span style="color: white; font-size: 1.5rem;">⏱</span>
            </div>
            <h3 style="font-size: 1rem; color: #374151; margin: 0 0 0.25rem 0;">15-20 Minutes</h3>
            <p style="font-size: 0.875rem; color: #6b7280; margin: 0;">Research questionnaire</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #dbeafe;
            height: 150px;
        ">
            <div style="
                background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            ">
                <span style="color: white; font-size: 1.5rem;">🔒</span>
            </div>
            <h3 style="font-size: 1rem; color: #374151; margin: 0 0 0.25rem 0;">Anonymous & Secure</h3>
            <p style="font-size: 0.875rem; color: #6b7280; margin: 0;">Academic research only</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application entry point with enhanced UI/UX."""
    favicon_path = Path(__file__).resolve().parent.parent / "assets" / "logos" / "favicon.png"
    st.set_page_config(
        page_title="AI Investment Advisory Research - UCT",
        page_icon=str(favicon_path),
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply comprehensive styling
    st.markdown(get_all_styles(), unsafe_allow_html=True)

    # Initialize session state
    initialize_state()
    st.session_state.current_page = "main"  # Set current page for progress tracking
    render_sidebar()

    # Check if informed consent has been given
    if not st.session_state.get("consent_given", False):
        # Welcome section with portrait
        portrait_path = Path(__file__).resolve().parent.parent / "assets" / "logos" / "Don_portrait.png"
        import base64
        
        # Load and encode the portrait image
        try:
            with open(portrait_path, "rb") as image_file:
                portrait_b64 = base64.b64encode(image_file.read()).decode()
                portrait_html = f"data:image/png;base64,{portrait_b64}"
        except:
            portrait_html = ""
        
        st.markdown(f"""
        <style>
        @media (max-width: 768px) {{
            .portrait-container {{
                display: none !important;
            }}
            .content-container {{
                flex-direction: column !important;
                text-align: center !important;
            }}
        }}
        </style>
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
            border-radius: 24px;
            padding: 2.5rem;
            margin: 2rem 0 3rem 0;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            border: 1px solid #e5e7eb;
        ">
            <div class="content-container" style="display: flex; align-items: center; gap: 2rem;">
                <div class="portrait-container" style="
                    flex-shrink: 0;
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    overflow: hidden;
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                    background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
                    padding: 3px;
                ">
                    <img src="{portrait_html}" style="
                        width: 100%;
                        height: 100%;
                        border-radius: 50%;
                        object-fit: cover;
                        background: white;
                    " alt="Don Kruger">
                </div>
                <div style="flex: 1;">
                    <h2 style="
                        color: #1e293b;
                        font-size: 1.875rem;
                        font-weight: 700;
                        margin: 0 0 0.75rem 0;
                        letter-spacing: -0.025em;
                    ">Howdy!</h2>
                    <p style="
                        color: #475569;
                        font-size: 1.125rem;
                        line-height: 1.75;
                        margin: 0 0 1rem 0;
                    ">
                        Thank you for taking the time to participate in this research. I appreciate it deeply and you are amazing.
                    </p>
                    <div style="
                        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
                        border: 1px solid #f59e0b;
                        border-radius: 12px;
                        padding: 1.25rem;
                        margin: 1rem 0;
                    ">
                        <h4 style="color: #92400e; margin: 0 0 0.75rem 0; font-size: 1rem;">
                            Please complete the following steps:
                        </h4>
                        <ol style="color: #78350f; margin: 0; padding-left: 1.25rem; line-height: 1.6;">
                            <li style="margin-bottom: 0.5rem;">
                                <strong>Experience the EasyAI system</strong> - Interact with the tool until you feel 
                                comfortable asking for investment advice
                            </li>
                            <li style="margin-bottom: 0.5rem;">
                                <strong>Keep your responses objective and honest</strong> - This ensures the scientific 
                                integrity of our evaluation
                            </li>
                            <li>
                                <strong>Complete survey</strong> - Come back here and complete the informed consent form to proceed with the survey.
                            </li>
                        </ol>
                    </div>
                    <div style="display: flex; gap: 1rem; margin: 1.25rem 0; flex-wrap: wrap;">
                        <a href="https://easyai.easyequities.io/" target="_blank" style="
                            display: inline-flex;
                            align-items: center;
                            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                            color: white;
                            padding: 0.75rem 1.25rem;
                            border-radius: 10px;
                            text-decoration: none;
                            font-weight: 600;
                            font-size: 0.9375rem;
                            box-shadow: 0 3px 12px rgba(16, 185, 129, 0.3);
                            transition: all 0.3s ease;
                            flex: 1;
                            min-width: 200px;
                            justify-content: center;
                        ">
                            <span style="margin-right: 0.5rem;">🤖</span>
                            Try EasyAI System First
                        </a>
                        <a href="https://www.researchgate.net/publication/390816837_Transforming_Investment_Advisory_with_Multi-Agent_RAG_Architectures_A_Design_Science_Approach" target="_blank" style="
                            display: inline-flex;
                            align-items: center;
                            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                            color: white;
                            padding: 0.75rem 1.25rem;
                            border-radius: 10px;
                            text-decoration: none;
                            font-weight: 600;
                            font-size: 0.9375rem;
                            box-shadow: 0 3px 12px rgba(139, 92, 246, 0.3);
                            transition: all 0.3s ease;
                            flex: 1;
                            min-width: 200px;
                            justify-content: center;
                        ">
                            <span style="margin-right: 0.5rem;">📄</span>
                            Read Research Paper (Optional)
                        </a>
                    </div>
                    <p style="
                        color: #64748b;
                        font-size: 0.975rem;
                        margin: 1rem 0 0 0;
                        font-style: italic;
                    ">
                        — Don Kruger, Researcher, UCT Information Systems
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced informed consent warning
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            border: 2px solid #fbbf24;
            border-radius: 20px;
            padding: 2.5rem;
            margin: 0 0 2rem 0;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -20px;
                right: -20px;
                width: 100px;
                height: 100px;
                background: radial-gradient(circle, rgba(251, 191, 36, 0.1) 0%, transparent 70%);
                border-radius: 50%;
            "></div>
            <div style="text-align: center;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                    border-radius: 16px;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
                ">
                    <span style="font-size: 2rem;">📋</span>
                </div>
                <h3 style="
                    color: #92400e;
                    font-size: 1.75rem;
                    font-weight: 700;
                    margin: 0 0 1rem 0;
                    letter-spacing: -0.025em;
                ">Informed Consent Required</h3>
                <p style="
                    color: #78350f;
                    font-size: 1.0625rem;
                    line-height: 1.75;
                    margin: 0 auto 2rem;
                    max-width: 600px;
                ">
                    Before participating in this research study, you must first read and provide informed consent.
                    This is required by the University of Cape Town's research ethics guidelines and ensures
                    you understand the study's purpose and your rights as a participant.
                </p>
                <div style="margin-top: 2rem;">
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Styled button container properly centered
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            # Apply custom CSS for the button
            st.markdown("""
            <style>
            div[data-testid="column"]:has(button[kind="primary"]) {
                display: flex;
                justify-content: center;
            }
            div.stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
                padding: 0.875rem 2rem;
                border-radius: 12px;
                font-weight: 600;
                font-size: 1.0625rem;
                box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
                transition: all 0.3s ease;
                border: none;
                width: 100%;
                height: auto;
            }
            div.stButton > button[kind="primary"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("📋 Read Informed Consent & Participate →", type="primary", use_container_width=True):
                st.switch_page('pages/1_Informed_Consent.py')
        
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # About section with enhanced design
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
                border: 1px solid #e5e7eb;
                min-height: 160px;
                display: flex;
                flex-direction: column;
            ">
                <div style="
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    width: 48px;
                    height: 48px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 0.75rem;
                    flex-shrink: 0;
                ">
                    <span style="color: white; font-size: 1.5rem;">🎓</span>
                </div>
                <h4 style="color: #1e293b; font-size: 1rem; margin: 0 0 0.5rem 0; font-weight: 600;">
                    Academic Research
                </h4>
                <p style="color: #64748b; font-size: 0.8125rem; margin: 0; line-height: 1.4;">
                    UCT Information Systems research project
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
                border: 1px solid #e5e7eb;
                min-height: 160px;
                display: flex;
                flex-direction: column;
            ">
                <div style="
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    width: 48px;
                    height: 48px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 0.75rem;
                    flex-shrink: 0;
                ">
                    <span style="color: white; font-size: 1.5rem;">🤖</span>
                </div>
                <h4 style="color: #1e293b; font-size: 1rem; margin: 0 0 0.5rem 0; font-weight: 600;">
                    AI Advisory Systems
                </h4>
                <p style="color: #64748b; font-size: 0.8125rem; margin: 0; line-height: 1.4;">
                    Evaluating multi-agent (agentic) AI flows
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
                border: 1px solid #e5e7eb;
                min-height: 160px;
                display: flex;
                flex-direction: column;
            ">
                <div style="
                    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                    width: 48px;
                    height: 48px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 0.75rem;
                    flex-shrink: 0;
                ">
                    <span style="color: white; font-size: 1.5rem;">🔒</span>
                </div>
                <h4 style="color: #1e293b; font-size: 1rem; margin: 0 0 0.5rem 0; font-weight: 600;">
                    Privacy Protected
                </h4>
                <p style="color: #64748b; font-size: 0.8125rem; margin: 0; line-height: 1.4;">
                    Anonymous & secure data handling
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.stop()
    
    # Hero section instead of plain title
    render_hero_section()
    
    # Information cards
    render_info_cards()
    
    # Add spacing
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Show consent confirmation
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 2rem;
    ">
        <div style="display: flex; align-items: center;">
            <span style="color: #065f46; font-size: 1.25rem; margin-right: 0.5rem;">✅</span>
            <div>
                <strong style="color: #065f46;">Consent Confirmed</strong>
                <span style="color: #047857; margin-left: 1rem;">
                    Participant: {st.session_state.get('consent_name', 'Anonymous')} • 
                    Date: {st.session_state.get('consent_date', 'Unknown')}
                </span>
            </div>
    </div>
</div>
    """, unsafe_allow_html=True)

    # Check if the investment research survey is configured
    if "investment_research" not in SPECS:
        st.error("Investment Research Survey is not configured. Please check the survey specifications.")
        st.stop()
    
    # Get the investment research survey
    spec = SPECS["investment_research"]
    st.session_state.survey_type = "investment_research"
    
    # Get namespace for this survey
    ns = current_namespace()

    # Progress indicator
    render_progress_bar()
    
    
    # Research questionnaire instructions
    with st.expander("📋 Research Questionnaire Instructions", expanded=False):
        # Add CSS for the rating scale
        st.markdown("""
        <style>
        .rating-scale-container {
            background: linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #0ea5e9;
        }
        .rating-scale-flex {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .rating-item {
            text-align: center;
        }
        .rating-circle {
            width: 40px;
            height: 40px;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
            font-weight: bold;
        }
        .rating-1 { background: #ef4444; }
        .rating-2 { background: #f59e0b; }
        .rating-3 { background: #6b7280; }
        .rating-4 { background: #3b82f6; }
        .rating-5 { background: #10b981; }
        .rating-label {
            color: #6b7280;
            font-size: 0.875rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Research Context")
        st.markdown("""
        This questionnaire evaluates your experience with AI-driven investment advisory systems. 
        Your responses will help researchers at UCT understand how to improve the transparency, 
        usability, and trustworthiness of AI financial recommendations.
        """)
        
        st.markdown("#### Rating Scale (1-5)")
        
        st.markdown("""
        <div class="rating-scale-container">
            <div class="rating-scale-flex">
                <div class="rating-item">
                    <div class="rating-circle rating-1">1</div>
                    <small class="rating-label">Strongly Disagree</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-2">2</div>
                    <small class="rating-label">Disagree</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-3">3</div>
                    <small class="rating-label">Neutral</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-4">4</div>
                    <small class="rating-label">Agree</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-5">5</div>
                    <small class="rating-label">Strongly Agree</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Research Guidelines")
        
        st.markdown("""
        - **Be honest and thoughtful** - Your genuine experience is valuable for research
        - **Provide specific examples** when possible in text responses
        - **Consider the AI system context** - You're evaluating experimental technology
        - **All responses are anonymous** - No personal information will be linked to your answers
        - **Take your time** - Quality responses are more valuable than speed
        - **Remember**: This is for academic research, not actual investment advice
        """)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0 1.5rem 0;
        ">
            <strong style="color: #92400e;">⚠️ Important Reminder:</strong>
            <span style="color: #78350f;"> This is experimental AI technology for research purposes only. 
            Do not make actual investment decisions based on any recommendations you encounter.</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Render the survey form with enhanced styling
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Add a subtle background for the form section
    st.markdown("""
    <div style="
        background: linear-gradient(180deg, transparent 0%, #fafbfc 100%);
        margin: 0 -3rem;
        padding: 2rem 3rem;
        border-radius: 24px 24px 0 0;
    ">
    """, unsafe_allow_html=True)

    render_form(spec, ns)

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Store the survey title for downstream use
    st.session_state["survey_display_name"] = spec.title
    
    # Enhanced navigation button
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <style>
        .big-button {
            background: linear-gradient(135deg, #1e3ea2 0%, #1a3491 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            font-size: 1.125rem;
            box-shadow: 0 4px 12px rgba(30, 62, 162, 0.3);
            transition: all 0.3s ease;
            display: block;
            text-decoration: none;
            margin: 2rem auto;
        }
        .big-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(30, 62, 162, 0.4);
            background: linear-gradient(135deg, #1a3491 0%, #162d80 100%);
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.page_link(
            'pages/3_Declaration_and_Submit.py',
            label='Continue to Review & Submit →'
        )
    
    # Add some spacing at the bottom
    st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 