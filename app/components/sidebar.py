# app/components/sidebar.py

from pathlib import Path
import streamlit as st
from app.utils import svg_image_html

def render_sidebar():
    """Renders the sidebar with custom page navigation."""
    # CSS to hide native Streamlit page navigation
    hide_native_nav_css = """
    <style>
    /* Hide native Streamlit page navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
    """
    st.markdown(hide_native_nav_css, unsafe_allow_html=True)
    
    # Sidebar styling: background, z-index positioning, and mobile view fixes
    # Includes dark-mode friendly variant via prefers-color-scheme
    sidebar_bg_css = """
    <style>
    [data-testid=\"stSidebar\"],
    [data-testid=\"stSidebar\"] > div:first-child {
        background: linear-gradient(135deg, #f5fbff 0%, #eaf6ff 100%) !important;
        background-color: #f5fbff !important;
        opacity: 1 !important;
        z-index: 999999 !important;
        position: relative !important;
    }
    
    /* Ensure sidebar content appears above main content */
    [data-testid=\"stSidebar\"] .css-1d391kg,
    [data-testid=\"stSidebar\"] .stVerticalBlock,
    [data-testid=\"stSidebar\"] > div {
        z-index: 999999 !important;
    }
    
    /* Ensure main content area stays behind sidebar */
    .main .block-container,
    [data-testid=\"stMain\"],
    [data-testid=\"stMain\"] .main,
    [data-testid=\"stMain\"] .block-container {
        z-index: 1 !important;
        position: relative !important;
    }
    
    /* Ensure custom HTML elements stay behind sidebar */
    .getting-started-card,
    .progress-warning,
    div[style*="background:"],
    div[style*="background-color:"] {
        z-index: 1 !important;
        position: relative !important;
    }
    
    /* Make sidebar navigation text white - comprehensive targeting */
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] a *,
    [data-testid="stSidebar"] a p,
    [data-testid="stSidebar"] a span,
    [data-testid="stSidebar"] a div,
    [data-testid="stSidebar"] .stPageLink-NavLink,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"],
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] *,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] span,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] div,
    [data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"],
    [data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"] *,
    [data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"] p,
    [data-testid="stSidebar"] div[data-testid="stPageLink-NavLink"] span,
    [data-testid="stSidebar"] .st-emotion-cache-1rtdyuf,
    [data-testid="stSidebar"] .st-emotion-cache-1rtdyuf *,
    [data-testid="stSidebar"] .st-emotion-cache-1rtdyuf p,
    [data-testid="stSidebar"] button[kind="pageLink"],
    [data-testid="stSidebar"] button[kind="pageLink"] *,
    [data-testid="stSidebar"] button[kind="pageLink"] p,
    [data-testid="stSidebar"] button[kind="pageLink"] span,
    [data-testid="stSidebar"] button[kind="pageLink"] div,
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] .stButton > button *,
    [data-testid="stSidebar"] .stButton > button p,
    [data-testid="stSidebar"] .stButton > button span {
        color: white !important;
        text-decoration: none !important;
    }
    
    /* Hover effects for sidebar navigation */
    [data-testid="stSidebar"] a:hover,
    [data-testid="stSidebar"] a:hover *,
    [data-testid="stSidebar"] .stPageLink-NavLink:hover,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover,
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover *,
    [data-testid="stSidebar"] button[kind="pageLink"]:hover,
    [data-testid="stSidebar"] button[kind="pageLink"]:hover *,
    [data-testid="stSidebar"] .stButton > button:hover,
    [data-testid="stSidebar"] .stButton > button:hover * {
        color: #e0f4ff !important;
        text-decoration: none !important;
    }
    
    /* Universal sidebar text color override - catch-all approach */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Ensure sidebar text elements are visible */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Mobile view specific fixes */
    @media (max-width: 768px) {
        [data-testid=\"stSidebar\"] {
            z-index: 999999 !important;
            position: fixed !important;
        }
        
        /* Ensure sidebar overlay works properly on mobile */
        [data-testid=\"stSidebar\"][aria-expanded=\"true\"] {
            z-index: 999999 !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            height: 100vh !important;
            width: 100% !important;
            max-width: 21rem !important;
            background: linear-gradient(135deg, #f5fbff 0%, #eaf6ff 100%) !important;
            background-color: #f5fbff !important;
            opacity: 1 !important;
        }
        
        /* Mobile dark mode sidebar */
        @media (prefers-color-scheme: dark) {
            [data-testid=\"stSidebar\"][aria-expanded=\"true\"] {
                background: linear-gradient(135deg, rgba(15, 188, 227, 0.95) 0%, rgba(60, 102, 164, 0.95) 100%) !important;
                background-color: rgba(30, 39, 46, 0.95) !important;
            }
        }
        
        /* Ensure main content is properly layered on mobile */
        .main .block-container,
        [data-testid=\"stMain\"] {
            z-index: 1 !important;
            position: relative !important;
        }
    }
    
    @media (prefers-color-scheme: dark) {
      [data-testid=\"stSidebar\"],
      [data-testid=\"stSidebar\"] > div:first-child {
          background: linear-gradient(135deg, rgba(15, 188, 227, 0.95) 0%, rgba(60, 102, 164, 0.95) 100%) !important;
          background-color: rgba(30, 39, 46, 0.95) !important;
          opacity: 1 !important;
          z-index: 999999 !important;
      }
    }
    </style>
    """
    st.markdown(sidebar_bg_css, unsafe_allow_html=True)
    
    with st.sidebar:
        # Logo at the top of sidebar
        logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "stx_svg.svg"
        if logo_path.exists():
            st.image(str(logo_path), width=240)
        
        st.markdown("---")
        
        # Custom page navigation with proper labels and icons
        # Paths must be relative to the app directory
        st.page_link('main.py', label='Capture Info')
        st.page_link('pages/1_AI_Assistance.py', label='AI Assistance', icon='🤖')
        st.page_link('pages/3_Declaration_and_Submit.py', label='Declaration & Submit') 