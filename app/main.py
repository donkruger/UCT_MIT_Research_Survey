"""
Main entry point for the Investment Decision-Making Research Survey Application.

This module provides the main survey form page with modern UI/UX design.
"""

from __future__ import annotations
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.styling import get_all_styles
from app.components.sidebar import render_sidebar
from app.utils import initialize_state, persist_text_input
from app.trading_sheet_parser import process_uploaded_file

def show_api_status():
    """Display API connection status in the sidebar."""
    try:
        from app.api.trade_client import TradeAllocationsClient
        client = TradeAllocationsClient()
        
        # Test connection
        if client.test_connection():
            # Custom styled success message that's visible on red background
            st.sidebar.markdown(f"""
            <div style="
                background: rgba(34, 197, 94, 0.15);
                border: 1px solid rgba(34, 197, 94, 0.3);
                border-radius: 8px;
                padding: 0.75rem;
                margin: 0.5rem 0;
                color: rgba(34, 197, 94, 1);
                font-weight: 500;
                backdrop-filter: blur(10px);
            ">
                &#10003; API Connected ({client.environment.upper()})
            </div>
            """, unsafe_allow_html=True)
        else:
            # Custom styled warning message
            st.sidebar.markdown(f"""
            <div style="
                background: rgba(251, 191, 36, 0.15);
                border: 1px solid rgba(251, 191, 36, 0.3);
                border-radius: 8px;
                padding: 0.75rem;
                margin: 0.5rem 0;
                color: rgba(251, 191, 36, 1);
                font-weight: 500;
                backdrop-filter: blur(10px);
            ">
                &#9888; API Connection Issue
            </div>
            <div style="
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.875rem;
                margin-top: 0.25rem;
            ">
                Check configuration in .streamlit/secrets.toml
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        # Custom styled error message
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            color: rgba(239, 68, 68, 1);
            font-weight: 500;
            backdrop-filter: blur(10px);
        ">
            &#10007; API Not Configured
        </div>
        <div style="
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        ">
            Configure in .streamlit/secrets.toml
        </div>
        """, unsafe_allow_html=True)

def render_progress_bar():
    """Render a beautiful progress indicator with 3-step process."""
    # Calculate progress based on trading sheet upload status
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
            <span style="font-size: 0.875rem; color: #ed1847; font-weight: 600;">
                Trading Process Progress
            </span>
            <span style="font-size: 0.875rem; color: #c41230;">
                Step 2 of 3 • Upload {int(questionnaire_progress * 100)}% Complete
            </span>
        </div>
        <div style="
            background: rgba(237, 24, 71, 0.1);
            border-radius: 8px;
            height: 8px;
            overflow: hidden;
            position: relative;
        ">
            <div style="
                background: linear-gradient(90deg, #ed1847 0%, #c41230 100%);
                height: 100%;
                width: {overall_progress * 100}%;
                border-radius: 8px;
                transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 4px rgba(237, 24, 71, 0.3);
            "></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.75rem; color: #64748b;">
            <span>&#10003; Declaration Given</span>
            <span>{'&#10003; Upload Complete' if questionnaire_progress >= 1.0 else '◦ Upload In Progress'}</span>
            <span>◦ Ready to Submit</span>
        </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def render_hero_section():
    """Render an impressive hero section."""
    hero_html = """
    <div style="
        background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
        border-radius: 24px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(237, 24, 71, 0.2);
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
        ">EasyEquities Trading</div>
        <h1 style="
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0 0 1rem 0;
            letter-spacing: -0.02em;
            position: relative;
        ">Trading Sheet Upload</h1>
        <p style="
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.125rem;
            line-height: 1.75;
            margin: 0;
            position: relative;
        ">
            EasyEquities Trading Operations • Accounts Processor API<br>
            Upload Unit Trust trading sheets for secure batch processing
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
            border: 1px solid #fee2e2;
            height: 150px;
            transition: all 0.3s ease;
        ">
            <div style="
                background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            ">
                <span style="color: white; font-size: 1.5rem;">◫</span>
            </div>
            <h3 style="font-size: 1rem; color: #374151; margin: 0 0 0.25rem 0;">Unit Trust Trades</h3>
            <p style="font-size: 0.875rem; color: #6b7280; margin: 0;">Upload Excel or CSV trading sheets</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #fee2e2;
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
                <span style="color: white; font-size: 1.5rem;">⚡</span>
            </div>
            <h3 style="font-size: 1rem; color: #374151; margin: 0 0 0.25rem 0;">Fast Processing</h3>
            <p style="font-size: 0.875rem; color: #6b7280; margin: 0;">Automated API validation & execution</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #fee2e2;
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
                <span style="color: white; font-size: 1.5rem;">⚿</span>
            </div>
            <h3 style="font-size: 1rem; color: #374151; margin: 0 0 0.25rem 0;">Secure & Compliant</h3>
            <p style="font-size: 0.875rem; color: #6b7280; margin: 0;">Encrypted transmission & audit trails</p>
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
    
    # Additional red button styling to override Streamlit defaults
    st.markdown("""
    <style>
    /* Override Streamlit primary button colors with EasyEquities red theme */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #ed1847 0%, #c41230 100%) !important;
        border: none !important;
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #f04568 0%, #ed1847 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(237, 24, 71, 0.3) !important;
    }

    .stButton > button[kind="primary"]:active,
    .stButton > button[data-testid="baseButton-primary"]:active {
        background: linear-gradient(135deg, #c41230 0%, #a00e26 100%) !important;
        transform: translateY(0) !important;
    }

    /* Ensure all buttons use the red theme */
    button[data-baseweb="button"][kind="primary"] {
        background: linear-gradient(135deg, #ed1847 0%, #c41230 100%) !important;
    }

    button[data-baseweb="button"][kind="primary"]:hover {
        background: linear-gradient(135deg, #f04568 0%, #ed1847 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    initialize_state()
    st.session_state.current_page = "main"  # Set current page for progress tracking
    render_sidebar()
    
    # Show API status in sidebar
    show_api_status()

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
            <div class="content-container">
                    <h2 style="
                        color: #1e293b;
                        font-size: 1.875rem;
                        font-weight: 700;
                        margin: 0 0 0.75rem 0;
                        letter-spacing: -0.025em;
                    ">Welcome to Trading Sheet</h2>
                    <p style="
                        color: #475569;
                        font-size: 1.125rem;
                        line-height: 1.75;
                        margin: 0 0 1rem 0;
                    ">
                        Your gateway to the EasyEquities Accounts Processor API. Upload trading sheets to execute Unit Trust (UT) trades seamlessly.
                    </p>
                    <div style="
                        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
                        border: 1px solid #f59e0b;
                        border-radius: 12px;
                        padding: 1.25rem;
                        margin: 1rem 0;
                    ">
                        <h4 style="color: #92400e; margin: 0 0 0.75rem 0; font-size: 1rem;">
                            Getting Started:
                        </h4>
                        <ol style="color: #78350f; margin: 0; padding-left: 1.25rem; line-height: 1.6;">
                            <li style="margin-bottom: 0.75rem;">
                                <strong>Prepare your trading sheet</strong> - Ensure your spreadsheet contains the required 
                                Unit Trust (UT) trading data in the proper format for processing through the Accounts Processor API.
                            </li>
                            <li style="margin-bottom: 0.75rem;">
                                <strong>Upload and process</strong> - Use the interface below to upload your trading sheet. 
                                The system will validate and process your trades through the EasyEquities allocations API.
                            </li>
                            <li>
                                <strong>Monitor execution</strong> - Track the status of your trades and ensure all 
                                Unit Trust transactions are processed correctly through the system.
                            </li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Trading Authorization Section
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
                    background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
                    border-radius: 16px;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 12px rgba(237, 24, 71, 0.3);
                ">
                    <span style="font-size: 2rem;">🛡</span>
                </div>
                <h3 style="
                    color: #92400e;
                    font-size: 1.75rem;
                    font-weight: 700;
                    margin: 0 0 1rem 0;
                    letter-spacing: -0.025em;
                ">Declaration Required</h3>
                <p style="
                    color: #78350f;
                    font-size: 1.0625rem;
                    line-height: 1.75;
                    margin: 0 auto 2rem;
                    max-width: 600px;
                ">
                    Before uploading your trading sheet, you must complete the declaration confirming
                    that all trading data is accurate, timely, and authorized for processing through
                    the EasyEquities Accounts Processor API.
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
                background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
                color: white;
                padding: 0.875rem 2rem;
                border-radius: 12px;
                font-weight: 600;
                font-size: 1.0625rem;
                box-shadow: 0 4px 16px rgba(237, 24, 71, 0.3);
                transition: all 0.3s ease;
                border: none;
                width: 100%;
                height: auto;
            }
            div.stButton > button[kind="primary"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(237, 24, 71, 0.4);
                background: linear-gradient(135deg, #c41230 0%, #a30f28 100%);
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("&#10003; Complete Declaration & Continue →", type="primary", use_container_width=True):
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
                    background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
                    width: 48px;
                    height: 48px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 0.75rem;
                    flex-shrink: 0;
                ">
                    <span style="color: white; font-size: 1.5rem;">⚿</span>
                </div>
                <h4 style="color: #1e293b; font-size: 1rem; margin: 0 0 0.5rem 0; font-weight: 600;">
                    Secure Processing
                </h4>
                <p style="color: #64748b; font-size: 0.8125rem; margin: 0; line-height: 1.4;">
                    Encrypted API connection for safe trade execution
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
                    <span style="color: white; font-size: 1.5rem;">&#8599;</span>
                </div>
                <h4 style="color: #1e293b; font-size: 1rem; margin: 0 0 0.5rem 0; font-weight: 600;">
                    Batch Processing
                </h4>
                <p style="color: #64748b; font-size: 0.8125rem; margin: 0; line-height: 1.4;">
                    Upload multiple Unit Trust trades at once
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
                    <span style="color: white; font-size: 1.5rem;">≡</span>
                </div>
                <h4 style="color: #1e293b; font-size: 1rem; margin: 0 0 0.5rem 0; font-weight: 600;">
                    Audit Trail
                </h4>
                <p style="color: #64748b; font-size: 0.8125rem; margin: 0; line-height: 1.4;">
                    Complete transaction history and tracking
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
    
    # Show declaration confirmation
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 2rem;
    ">
        <div style="display: flex; align-items: center;">
            <span style="color: #065f46; font-size: 1.25rem; margin-right: 0.5rem;">&#10003;</span>
            <div>
                <strong style="color: #065f46;">Declaration Confirmed</strong>
                <span style="color: #047857; margin-left: 1rem;">
                    Authorized by: {st.session_state.get('consent_name', 'Anonymous')} • 
                    Date: {st.session_state.get('consent_date', 'Unknown')}
                </span>
            </div>
    </div>
</div>
    """, unsafe_allow_html=True)

    # Initialize trading sheet session
    st.session_state.trading_type = "unit_trust"
    st.session_state["survey_display_name"] = "Unit Trust Trading Sheet"

    # Progress indicator
    render_progress_bar()
    
    
    # Trading Sheet Upload Instructions
    with st.expander("≡ Trading Sheet Upload Instructions", expanded=False):
        # Add CSS for the rating scale
        st.markdown("""
        <style>
        .rating-scale-container {
            background: linear-gradient(90deg, #fff5f5 0%, #fee2e2 50%, #fff5f5 100%);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid #ed1847;
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
        .rating-1 { background: #ed1847; }
        .rating-2 { background: #d91845; }
        .rating-3 { background: #c41843; }
        .rating-4 { background: #b01841; }
        .rating-5 { background: #9c183f; }
        .rating-label {
            color: #6b7280;
            font-size: 0.875rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Trading Sheet Format Requirements")
        st.markdown("""
        Your trading sheet must be properly formatted for processing through the Accounts Processor API. 
        Ensure all Unit Trust trade data includes required fields and follows the prescribed format 
        for successful execution.
        """)
        
        st.markdown("#### Required Columns for Trading Sheet")
        
        st.markdown("""
        <div class="rating-scale-container">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-bottom: 1rem;">
                <div class="rating-item">
                    <div class="rating-circle rating-1">1</div>
                    <small class="rating-label">ShareCode</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-2">2</div>
                    <small class="rating-label">ContractCode</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-3">3</div>
                    <small class="rating-label">InstrumentID</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-4">4</div>
                    <small class="rating-label">Units</small>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem;">
                <div class="rating-item">
                    <div class="rating-circle rating-5">5</div>
                    <small class="rating-label">Amount</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-1">6</div>
                    <small class="rating-label">Direction</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-2">7</div>
                    <small class="rating-label">UserID</small>
                </div>
                <div class="rating-item">
                    <div class="rating-circle rating-3">8</div>
                    <small class="rating-label">TrustAccount</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Trading Sheet Guidelines")
        
        st.markdown("""
        - **File Format** - Excel (.xlsx) or CSV format accepted
        - **Column Headers** - Must match exactly: ShareCode, ContractCode, InstrumentID, Units, Amount, Direction, UserID, TrustAccount
        - **Data Validation** - All 8 columns must be populated for each trade
        - **Direction Values** - BUY or SELL transactions only
        - **Numeric Format** - Units and Amount as decimal values (no currency symbols)
        - **ShareCode** - Fund identifier (e.g., NGWINT)
        - **ContractCode** - Full contract identifier (e.g., UT.ZA.NGWINT)
        - **Processing Time** - Trades are typically processed within 24 hours
        """)
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0 1.5rem 0;
        ">
            <strong style="color: #92400e;">&#9888; Important Notice:</strong>
            <span style="color: #78350f;"> All trades submitted will be executed as specified. 
            Please double-check all trade details before uploading your sheet.</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Trading Sheet Upload Section
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # Upload Section with modern card design
    st.markdown("""
    <div style="
        background: white;
        border-radius: 24px;
        padding: 2.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #fee2e2;
        margin-bottom: 2rem;
    ">
        <h2 style="
            color: #1e293b;
            font-size: 1.75rem;
            font-weight: 700;
            margin: 0 0 1rem 0;
            display: flex;
            align-items: center;
        ">
            <span style="
                background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
                color: white;
                width: 48px;
                height: 48px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 1rem;
                font-size: 1.5rem;
            ">◫</span>
            Upload Trading Sheet
        </h2>
        <p style="
            color: #64748b;
            font-size: 1.0625rem;
            line-height: 1.6;
            margin: 0 0 1.5rem 0;
        ">
            Upload your Unit Trust trading sheet in Excel (.xlsx) or CSV format for processing.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # File uploader widget
    uploaded_file = st.file_uploader(
        "Choose your trading sheet file",
        type=['xlsx', 'xls', 'csv'],
        help="Select an Excel or CSV file containing your Unit Trust trading data",
        key="trading_sheet_upload"
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        # Store file info in session state
        st.session_state['uploaded_file_name'] = uploaded_file.name
        st.session_state['uploaded_file_size'] = uploaded_file.size
        st.session_state['file_uploaded'] = True
        st.session_state['upload_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Parse the uploaded file
        file_content = uploaded_file.read()
        success, result = process_uploaded_file(file_content, uploaded_file.name)
        
        if success:
            # Store parsed data in session state
            st.session_state['parsed_trading_data'] = result['data']
            st.session_state['trading_data_display'] = result['display_data']
            st.session_state['trading_data_summary'] = result['summary']
            st.session_state['trading_data_validation'] = result['validation']
            st.session_state['trading_parser'] = result['parser']
            
            # Clear any previous UT protection block
            if 'ut_protection_blocked' in st.session_state:
                del st.session_state['ut_protection_blocked']
            
            # File info display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                    border-radius: 12px;
                    padding: 1rem;
                    border: 1px solid #86efac;
                ">
                    <p style="color: #065f46; margin: 0; font-size: 0.875rem;">File Name</p>
                    <p style="color: #047857; margin: 0.25rem 0 0 0; font-weight: 600;">""" + uploaded_file.name + """</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                file_size_kb = uploaded_file.size / 1024
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border-radius: 12px;
                    padding: 1rem;
                    border: 1px solid #7dd3fc;
                ">
                    <p style="color: #0c4a6e; margin: 0; font-size: 0.875rem;">File Size</p>
                    <p style="color: #0369a1; margin: 0.25rem 0 0 0; font-weight: 600;">{file_size_kb:.2f} KB</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                    border-radius: 12px;
                    padding: 1rem;
                    border: 1px solid #fbbf24;
                ">
                    <p style="color: #78350f; margin: 0; font-size: 0.875rem;">Trades Found</p>
                    <p style="color: #92400e; margin: 0.25rem 0 0 0; font-weight: 600;">{result['summary']['total_trades']} Records</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Preview section
            st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
            
            with st.expander("▦ Preview Trading Data", expanded=True):
                # Show summary statistics
                summary = result['summary']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Buy Trades", summary['buy_trades'])
                with col2:
                    st.metric("Sell Trades", summary['sell_trades'])
                with col3:
                    st.metric("Unique Shares", summary['unique_shares'])
                
                # Display the first 5 rows of data in a table
                if 'parsed_trading_data' in st.session_state and not st.session_state.parsed_trading_data.empty:
                    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                    st.markdown("**Trading Data Preview (First 5 rows):**")
                    
                    # Use st.dataframe for robust table rendering
                    st.dataframe(st.session_state.parsed_trading_data.head())
                    
                    if len(st.session_state.parsed_trading_data) > 5:
                        st.info(f"Showing 5 of {len(st.session_state.parsed_trading_data)} total trades. Full data will be displayed on the Review & Submit page.")
            
            # Show validation warnings if any
            if result['validation']['warnings']:
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                with st.expander("&#9888; Validation Warnings", expanded=False):
                    for warning in result['validation']['warnings']:
                        st.warning(warning)
            
            # Validation status - Success
            st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border: 2px solid #10b981;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 2rem;
            ">
                <div style="display: flex; align-items: center;">
                    <span style="color: #065f46; font-size: 1.5rem; margin-right: 1rem;">&#10003;</span>
                    <div>
                        <h4 style="color: #065f46; margin: 0 0 0.25rem 0;">File Validated Successfully</h4>
                        <p style="color: #047857; margin: 0;">
                            {result['summary']['total_trades']} trades parsed and validated. Ready for processing.
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Parsing failed - show errors
            st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                border: 2px solid #ef4444;
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 2rem;
            ">
                <div style="display: flex; align-items: start;">
                    <span style="color: #991b1b; font-size: 1.5rem; margin-right: 1rem;">&#10007;</span>
                    <div style="width: 100%;">
                        <h4 style="color: #991b1b; margin: 0 0 0.75rem 0;">File Validation Failed</h4>
                        <p style="color: #dc2626; margin: 0 0 1rem 0;">
                            The uploaded file could not be processed due to the following errors:
                        </p>
            """, unsafe_allow_html=True)
            
            # Check for UT protection errors specifically
            ut_protection_errors = [error for error in result['errors'] if 'SECURITY BLOCK: Non-Unit Trust trades detected' in error]
            
            if ut_protection_errors:
                # SECURITY BLOCK: Special handling for UT protection violations
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                    border: 3px solid #dc2626;
                    border-radius: 16px;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    position: relative;
                ">
                    <div style="display: flex; align-items: start;">
                        <span style="color: #991b1b; font-size: 2rem; margin-right: 1rem;">⊞</span>
                        <div style="width: 100%;">
                            <h3 style="color: #991b1b; margin: 0 0 1rem 0; font-size: 1.5rem; font-weight: 700;">
                                SECURITY PROTECTION ACTIVE
                            </h3>
                            <div style="
                                background: white;
                                border: 2px solid #dc2626;
                                border-radius: 12px;
                                padding: 1.5rem;
                                margin-bottom: 1.5rem;
                            ">
                                <h4 style="color: #991b1b; margin: 0 0 1rem 0;">Unit Trust Only Enforcement</h4>
                                <p style="color: #dc2626; margin: 0 0 1rem 0; font-weight: 500;">
                                    This application is configured to process <strong>Unit Trust (UT) trades only</strong>. 
                                    Non-UT trades have been detected and blocked for security and compliance reasons.
                                </p>
                """, unsafe_allow_html=True)
                
                # Display the detailed error message from the parser
                for error in ut_protection_errors:
                    st.markdown(f"""
                                <div style="
                                    background: #fef2f2;
                                    border-left: 4px solid #dc2626;
                                    padding: 1rem;
                                    margin: 1rem 0;
                                    border-radius: 4px;
                                    font-family: monospace;
                                    font-size: 0.875rem;
                                    white-space: pre-line;
                                ">
                                    {error}
                                </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                                <div style="
                                    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                                    border: 2px solid #f59e0b;
                                    border-radius: 8px;
                                    padding: 1.25rem;
                                    margin: 1rem 0;
                                ">
                                    <h4 style="color: #92400e; margin: 0 0 0.75rem 0;">&#10003; How to Fix This Issue:</h4>
                                    <ol style="color: #78350f; margin: 0; padding-left: 1.25rem; line-height: 1.6;">
                                        <li style="margin-bottom: 0.5rem;">
                                            <strong>Review your trading sheet</strong> - Identify all non-UT trades
                                        </li>
                                        <li style="margin-bottom: 0.5rem;">
                                            <strong>Remove invalid contracts</strong> - Keep only UT.ZA.* ContractCodes
                                        </li>
                                        <li style="margin-bottom: 0.5rem;">
                                            <strong>Verify format compliance</strong> - Ensure UT.ZA.{{ShareCode}} pattern
                                        </li>
                                        <li>
                                            <strong>Re-upload your corrected file</strong> - The system will re-validate
                                        </li>
                                    </ol>
                                </div>
                                
                                <div style="
                                    background: #f8fafc;
                                    border: 1px solid #e2e8f0;
                                    border-radius: 8px;
                                    padding: 1rem;
                                    margin: 1rem 0;
                                    text-align: center;
                                ">
                                    <p style="color: #475569; margin: 0; font-size: 0.875rem;">
                                        <strong>Need Assistance?</strong><br>
                                        Contact the Trading Desk • Include this timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # SECURITY: Force navigation disable
                st.session_state['ut_protection_blocked'] = True
            else:
                # Display other validation errors normally
                for error in result['errors']:
                    st.markdown(f"""
                            <div style="
                                background: white;
                                border-left: 4px solid #ef4444;
                                padding: 0.75rem;
                                margin-bottom: 0.5rem;
                                border-radius: 4px;
                            ">
                                <p style="color: #991b1b; margin: 0; font-size: 0.875rem;">• {error}</p>
                            </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("""
                        <p style="color: #dc2626; margin: 1rem 0 0 0; font-size: 0.875rem;">
                            Please correct these issues and upload the file again.
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Clear invalid data from session state
            if 'parsed_trading_data' in st.session_state:
                del st.session_state['parsed_trading_data']
            if 'trading_data_display' in st.session_state:
                del st.session_state['trading_data_display']
            if 'trading_data_summary' in st.session_state:
                del st.session_state['trading_data_summary']
            if 'trading_parser' in st.session_state:
                del st.session_state['trading_parser']
        
    else:
        # No file uploaded yet
        st.markdown("""
        <div style="
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 16px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
        ">
            <div style="
                background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
                color: white;
                width: 80px;
                height: 80px;
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1.5rem;
                font-size: 2.5rem;
            ">→</div>
            <h3 style="color: #475569; margin: 0 0 0.75rem 0;">No File Selected</h3>
            <p style="color: #64748b; margin: 0 0 1.5rem 0;">
                Please upload your Unit Trust trading sheet to continue
            </p>
            <p style="color: #94a3b8; font-size: 0.875rem; margin: 0;">
                Supported formats: Excel (.xlsx, .xls) or CSV (.csv)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced navigation button
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <style>
        .big-button {
            background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            font-size: 1.125rem;
            box-shadow: 0 4px 12px rgba(237, 24, 71, 0.3);
            transition: all 0.3s ease;
            display: block;
            text-decoration: none;
            margin: 2rem auto;
        }
        .big-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(237, 24, 71, 0.4);
            background: linear-gradient(135deg, #c41230 0%, #a30f28 100%);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Only show navigation button if file is uploaded, parsed successfully, and not blocked by UT protection
        if (st.session_state.get('parsed_trading_data') is not None and 
            not st.session_state.get('ut_protection_blocked', False)):
            if st.button("Continue to Review & Submit →", 
                        type="primary", 
                        use_container_width=True,
                        help="Proceed to review trading data and submit to API"):
                st.switch_page('pages/3_Declaration_and_Submit.py')
        else:
            st.markdown("""
            <div style="
                background: #f3f4f6;
                border: 2px solid #9ca3af;
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
            ">
                <p style="margin: 0; color: #6b7280;">
                    Please upload a trading sheet to continue to the review step
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Add some spacing at the bottom
    st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 