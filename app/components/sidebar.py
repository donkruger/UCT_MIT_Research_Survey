"""
Sidebar component for the Research Survey Application with premium UI/UX design.
"""

import base64
from pathlib import Path
import streamlit as st
from app.utils import svg_image_html

def _get_logo_base64():
    """Get the UCT logo as base64 encoded string."""
    try:
        logo_path = Path(__file__).parent.parent.parent / "assets" / "logos" / "UCT_logo.png"
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        # Fallback to empty string if logo not found
        st.warning(f"Could not load UCT logo: {e}")
        return ""

def render_sidebar():
    """Renders the sidebar with modern, sophisticated design."""
    
    # Premium sidebar styling with glassmorphism effect
    sidebar_bg_css = """
    <style>
    /* Hide native Streamlit page navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Custom scrollbar for sidebar */
    [data-testid="stSidebar"]::-webkit-scrollbar {
        width: 6px;
    }
    
    [data-testid="stSidebar"]::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 3px;
    }
    
    [data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    /* Sidebar background with glassmorphism */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1e40af 0%, #1e3a8a 100%) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        position: relative !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Glass effect overlay */
    [data-testid="stSidebar"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, 
            rgba(30, 64, 175, 0.1) 0%, 
            rgba(59, 130, 246, 0.1) 100%);
        pointer-events: none;
        z-index: 1;
    }
    
    /* Content above glass effect */
    [data-testid="stSidebar"] > div {
        position: relative;
        z-index: 2;
    }
    
    /* Navigation link styling */
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        margin: 0.5rem 0 !important;
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
        text-decoration: none !important;
        display: block !important;
    }
    
    [data-testid="stSidebar"] a:hover,
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 12px rgba(74, 105, 255, 0.2) !important;
    }
    
    /* Active page indicator */
    [data-testid="stSidebar"] a[aria-current="page"] {
        background: linear-gradient(135deg, 
            rgba(74, 105, 255, 0.3) 0%, 
            rgba(139, 92, 246, 0.3) 100%) !important;
        border-color: rgba(74, 105, 255, 0.5) !important;
        box-shadow: 0 0 20px rgba(74, 105, 255, 0.2) !important;
    }
    
    /* Text color consistency */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label {
        color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Expander styling - ONLY for sidebar */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1rem !important;
    }
    
    /* Ensure main content expanders have light backgrounds - More specific selectors */
    .stApp .main .streamlit-expanderHeader,
    [data-testid="stMain"] .streamlit-expanderHeader,
    .main .element-container .streamlit-expanderHeader,
    div:not([data-testid="stSidebar"]) .streamlit-expanderHeader {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    
    .stApp .main .streamlit-expanderContent,
    [data-testid="stMain"] .streamlit-expanderContent,
    .main .element-container .streamlit-expanderContent,
    div:not([data-testid="stSidebar"]) .streamlit-expanderContent {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
    }
    
    /* Override any gradient backgrounds on main content expanders - Nuclear option */
    .stApp .main .streamlit-expanderHeader,
    [data-testid="stMain"] .streamlit-expanderHeader,
    .main .streamlit-expanderHeader,
    .element-container .streamlit-expanderHeader,
    .block-container .streamlit-expanderHeader {
        background-image: none !important;
        background: #f8fafc !important;
        background-color: #f8fafc !important;
    }
    
    /* Force override Streamlit's default expander styling */
    .streamlit-expanderHeader:not([data-testid="stSidebar"] .streamlit-expanderHeader) {
        background: #f8fafc !important;
        background-image: none !important;
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        color: #1e293b !important;
    }
    
    .streamlit-expanderContent:not([data-testid="stSidebar"] .streamlit-expanderContent) {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    
    /* Logo container */
    .sidebar-logo {
        text-align: center;
        padding: 2rem 1rem;
        position: relative;
        overflow: hidden;
    }
    
    .logo-bg {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(74, 105, 255, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: pulse 3s ease-in-out infinite;
    }
    
    .logo-content {
        position: relative;
        z-index: 2;
        animation: float 3s ease-in-out infinite;
    }
    
    .logo-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto 1rem;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(30, 64, 175, 0.3);
        overflow: hidden;
    }
    
    .logo-icon img {
        width: 150px;
        height: 150px;
        object-fit: contain;
        filter: brightness(1.2) contrast(1.1);
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        padding: 2px;
    }
    
    .logo-text {
        color: white;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .logo-title {
        color: white;
        font-size: 1.25rem;
        margin: 0.5rem 0 0.25rem 0;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    .logo-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.875rem;
        margin: 0;
    }
    
    /* Progress tracker */
    .progress-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.875rem;
        margin-bottom: 1.5rem;
        width: 100%;
        max-width: 100%;
        box-sizing: border-box;
        overflow: hidden;
    }
    
    .progress-title {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.875rem;
        margin: 0 0 0.5rem 0;
        font-weight: 500;
    }
    
    .progress-bar {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        height: 6px;
        overflow: hidden;
        margin-bottom: 0.75rem;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 10px rgba(30, 64, 175, 0.5);
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        max-width: 100%;
        overflow: hidden;
    }
    
    .progress-step {
        text-align: center;
        flex: 0 0 auto;
        min-width: 45px;
        max-width: 50px;
    }
    
    .step-circle {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        margin: 0 auto 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid;
    }
    
    .step-circle.active {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-color: #1e40af;
    }
    
    .step-circle.inactive {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .step-number {
        color: white;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .step-label {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.65rem;
        line-height: 1.2;
        word-break: break-word;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .step-connector {
        height: 2px;
        flex: 1;
        margin: 0 0.125rem 1rem;
        min-width: 15px;
        max-width: 30px;
    }
    
    .step-connector.active {
        background: linear-gradient(90deg, #1e40af, #3b82f6);
    }
    
    .step-connector.inactive {
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.3) !important;
      }
    }
    </style>
    """
    st.markdown(sidebar_bg_css, unsafe_allow_html=True)
    
    with st.sidebar:
        # Logo section using CSS classes
        st.markdown("""
        <div class="sidebar-logo">
            <div class="logo-bg"></div>
            <div class="logo-content">
                <div class="logo-icon">
                    <img src="data:image/png;base64,{}" alt="UCT Logo">
                </div>
                <h2 class="logo-title">UCT Research</h2>
                <p class="logo-subtitle">Design Science Study</p>
            </div>
        </div>
        """.format(_get_logo_base64()), unsafe_allow_html=True)
        
        # Divider
        st.markdown('<hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent); margin: 1.5rem 0;">', unsafe_allow_html=True)
        
        # Navigation section
        st.markdown("""
        <div style="padding: 0 0.5rem;">
            <p style="color: rgba(255, 255, 255, 0.5); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; font-weight: 600;">Navigation</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation links
        st.page_link('pages/1_Informed_Consent.py', label='📋 Informed Consent')
        st.page_link('main.py', label='📊 Research Questionnaire')
        st.page_link('pages/3_Declaration_and_Submit.py', label='✓ Review & Submit')
        
        # Divider
        st.markdown('<hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent); margin: 1.5rem 0;">', unsafe_allow_html=True)
        
        # Progress tracker with 3 steps: Consent → Questionnaire → Submit
        current_page = st.session_state.get("current_page", "consent")
        consent_given = st.session_state.get("consent_given", False)
        
        # Determine progress based on current state
        if not consent_given:
            progress = 0.0  # No consent yet
        elif current_page == "main" or consent_given:
            progress = 0.5  # Consent given, on questionnaire
        else:
            progress = 1.0  # On submit page
            
        # Check if we're on submit page
        if "3_Declaration_and_Submit" in str(st.session_state.get("current_page", "")):
            progress = 1.0
            
        progress_width = int(progress * 100)
        
        # Determine step classes for 3-step process
        step1_class = "active" if consent_given else "inactive"  # Consent
        step2_class = "active" if progress >= 0.5 else "inactive"  # Questionnaire
        step3_class = "active" if progress >= 1.0 else "inactive"  # Submit
        
        connector1_class = "active" if progress >= 0.5 else "inactive"  # Consent → Questionnaire
        connector2_class = "active" if progress >= 1.0 else "inactive"  # Questionnaire → Submit
        
        st.markdown(f"""
        <div class="progress-card">
            <p class="progress-title">Progress Tracker</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_width}%;"></div>
            </div>
            <div class="progress-steps">
                <div class="progress-step">
                    <div class="step-circle {step1_class}">
                        <span class="step-number">1</span>
                    </div>
                    <small class="step-label">Consent</small>
                </div>
                <div class="step-connector {connector1_class}"></div>
                <div class="progress-step">
                    <div class="step-circle {step2_class}">
                        <span class="step-number">2</span>
                    </div>
                    <small class="step-label">Survey</small>
                </div>
                <div class="step-connector {connector2_class}"></div>
                <div class="progress-step">
                    <div class="step-circle {step3_class}">
                        <span class="step-number">3</span>
                    </div>
                    <small class="step-label">Submit</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        