"""
Declaration & Acceptance page for Trading Sheet operations and compliance.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import bcrypt

# --- PAGE CONFIG ---
favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.png"
st.set_page_config(
    page_title="Login & Declaration - Trading Sheet",
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.sidebar import render_sidebar
from app.styling import get_all_styles
from app.utils import initialize_state, persist_checkbox, persist_text_input
from app.auth import authenticate, is_authenticated, get_current_user, get_remaining_lockout_time

# Initialize and apply styling
initialize_state()
st.session_state.current_page = "consent"  # Set current page for progress tracking
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

render_sidebar()

# Custom CSS for informed consent
st.markdown("""
<style>
.consent-header {
    background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
}

.institution-info {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border: 1px solid #cbd5e1;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.consent-section {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #e2e8f0;
    border-left: 4px solid #ed1847;
}

.consent-section h3 {
    color: #ed1847;
    margin-top: 0;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
}

.consent-icon {
    background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    font-size: 1rem;
}

.risk-warning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border: 2px solid #f59e0b;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.benefits-box {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border: 2px solid #10b981;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.signature-section {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 2px solid #0ea5e9;
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
}

.consent-checkbox {
    background: white;
    border: 2px solid #ed1847;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.proceed-button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 1rem 2rem;
    border-radius: 12px;
    border: none;
    font-weight: 600;
    font-size: 1.125rem;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
}

.proceed-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
}

.proceed-button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
    transform: none;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="consent-header">
    <h1 style="margin: 0 0 0.5rem 0; font-size: 2.25rem; color: white;">Trading Declaration & Acceptance</h1>
    <p style="margin: 0; font-size: 1.125rem; opacity: 0.95; color: white;">EasyEquities Accounts Processor API - Trading Sheet Submission</p>
</div>
""", unsafe_allow_html=True)

# Trading Platform Information with Jump to Bottom button
st.markdown("""
<div class="institution-info" style="position: relative;">
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
        <div style="display: flex; align-items: center;">
            <div style="background: linear-gradient(135deg, #ed1847 0%, #c41230 100%); color: white; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 1.25rem; font-weight: bold;">EE</div>
            <div>
                <h3 style="margin: 0; color: #ed1847;">EasyEquities Trading Operations</h3>
                <p style="margin: 0; color: #64748b;">Accounts Processor API • Unit Trust Trading System</p>
            </div>
        </div>
        <a href="#declaration-form" style="
            background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.25rem;
            font-size: 0.875rem;
            font-weight: 600;
            text-decoration: none;
            box-shadow: 0 2px 8px rgba(237, 24, 71, 0.25);
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(237, 24, 71, 0.35)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(237, 24, 71, 0.25)'">
            <span style="font-size: 1rem;">↓</span> Skip to Login
        </a>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
        <div>
            <strong>Support Team:</strong> Trading Operations<br>
            <strong>System:</strong> Accounts Processor API<br>
            <strong>Email:</strong> trading@easyequities.co.za
        </div>
        <div>
            <strong>Platform:</strong> EasyEquities Trading Sheet<br>
            <strong>Purpose:</strong> Unit Trust Trade Execution
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Trading Authorization Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">&#10003;</span>Trading Authorization</h3>
    <p>You are about to submit trading instructions through the EasyEquities Accounts Processor API. This system processes Unit Trust (UT) trades based on the trading sheet data you upload.</p>
    <p><strong>By proceeding, you authorize the execution of trades as specified in your trading sheet.</strong> The system will validate and process your instructions through the allocations trading API for Unit Trust transactions.</p>
    <p>Please ensure all trading data is accurate, complete, and reflects your intended trading instructions before submission.</p>
</div>
""", unsafe_allow_html=True)

# Trading Process Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">•</span>Trading Process</h3>
    <p>During the trading process, you will:</p>
    <ul>
        <li><strong>Upload your trading sheet</strong> containing Unit Trust trading instructions</li>
        <li><strong>System validation</strong> will verify data format and trading parameters</li>
        <li><strong>Execute trades</strong> through the Accounts Processor API</li>
    </ul>
    <p>Processing time varies based on the number and complexity of trades in your submission.</p>
</div>
""", unsafe_allow_html=True)

# Compliance & Risk Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">!</span>Important Trading Compliance</h3>
    <div class="risk-warning">
        <h4 style="color: #92400e; margin-top: 0;">⚠ Trading Risk Warning</h4>
        <p style="margin-bottom: 0;"><strong>You are responsible for ensuring all trading instructions are accurate, authorized, and comply with applicable regulations.</strong></p>
        <p style="margin-bottom: 0;"><strong>Submitted trades will be executed as specified. Please verify all data before submission as trades cannot be reversed once processed.</strong></p>
    </div>
    <p><em>The system processes trades exactly as submitted. Double-check all trading parameters and amounts before uploading your sheet.</em></p>
</div>
""", unsafe_allow_html=True)

# System Features Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">+</span>System Features</h3>
    <div class="benefits-box">
        <ul style="margin: 0;">
            <li>Streamlined processing of Unit Trust trades through the Accounts Processor API</li>
            <li>Automated validation of trading data to ensure format compliance</li>
            <li>Efficient batch processing of multiple trades from a single upload</li>
            <li>Real-time status tracking and execution confirmation</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Data Security Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">◊</span>Data Security & Audit Trail</h3>
    <ul>
        <li><strong>All trading data is encrypted</strong> during transmission and processing</li>
        <li><strong>Complete audit trail</strong> maintained for all trading activities</li>
        <li><strong>Access controls</strong> ensure only authorized personnel can process trades</li>
        <li><strong>Data retention</strong> complies with regulatory requirements</li>
        <li><strong>System logs</strong> track all operations for compliance and audit purposes</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Terms of Use Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">&#10003;</span>Terms of Use</h3>
    <p><strong>By using this system, you agree to:</strong></p>
    <ul>
        <li>Submit only authorized and accurate trading instructions</li>
        <li>Accept responsibility for all trades executed based on your submissions</li>
        <li>Comply with all applicable trading regulations and policies</li>
    </ul>
    <p><strong>The system reserves the right</strong> to reject or flag suspicious trading activities for review. All trades are subject to validation and compliance checks.</p>
</div>
""", unsafe_allow_html=True)

# Trade Confirmation Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">↵</span>Trade Confirmation</h3>
    <p>You will receive confirmation of all processed trades including execution status, timestamps, and reference numbers for tracking and audit purposes.</p>
</div>
""", unsafe_allow_html=True)

# Support Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">?</span>Support & Assistance</h3>
    <ul>
        <li>For technical issues with the Trading Sheet system, contact our support team</li>
        <li>Trading-related queries will be addressed by the operations team</li>
        <li><strong>Support:</strong> trading@easyequities.co.za</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Declaration & Signature Section
st.markdown("""
<div class="signature-section">
    <h3 style="color: #0ea5e9; margin-top: 0; text-align: center;">&#10003; Data Accuracy Declaration & Authorization</h3>
    <p style="text-align: center; margin-bottom: 2rem;"><em>By completing this section, you declare that all trading data is accurate and authorize its processing.</em></p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
    <p><strong>The trading process, validation requirements, and system capabilities have been explained in this form.</strong></p>
    <p>By proceeding, you confirm that all trading data you submit is accurate, timely, and authorized for execution through the EasyEquities Accounts Processor API.</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# AUTHENTICATION SECTION
# ============================================

# Check if user is already authenticated
if not is_authenticated():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ed1847 0%, #c41230 100%); color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
        <h3 style="color: white; margin: 0;">⚿ Authentication Required</h3>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0;">Please login to continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout for login and password generator
    left_col, right_col = st.columns(2, gap="large")
    
    # LEFT COLUMN: Existing Login Form
    with left_col:
        st.markdown("### 🔐 Secure Login")
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        login_email = st.text_input(
            "Email Address *",
            key="login_email",
            placeholder="your.email@example.com",
            help="Enter your authorized email address"
        )
        
        # Password field (uses Streamlit's built-in show/hide toggle)
        login_password = st.text_input(
            "Password *",
            key="login_password",
            type="password",
            placeholder="Enter your password",
            help="Your secure password"
        )
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Login button
        if st.button("⚿ Login", type="primary", use_container_width=True):
            if not login_email or not login_password:
                st.error("✗ Please enter both email and password")
            else:
                # Check for rate limiting
                lockout_time = get_remaining_lockout_time(login_email)
                if lockout_time:
                    minutes = lockout_time // 60
                    seconds = lockout_time % 60
                    st.error(f"⚿ Too many failed attempts. Please wait {minutes}m {seconds}s before trying again.")
                else:
                    # Attempt authentication
                    if authenticate(login_email, login_password):
                        st.success("✓ Login successful! Welcome back.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("✗ Invalid email or password. Please try again.")
    
    # RIGHT COLUMN: Password Hash Generator for DevOps
    with right_col:
        st.markdown('<a id="declaration-form"></a>', unsafe_allow_html=True)
        st.markdown("###  Account Management")
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # Expandable information card
        with st.expander("ℹ️ **Create an account or reset your password as follows**", expanded=False):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                        border-left: 4px solid #f59e0b; 
                        padding: 1rem; 
                        border-radius: 8px;
                        margin-bottom: 1rem;">
                <p style="margin: 0; color: #78350f;"><strong>⚠️ Please Read Carefully:</strong></p>
                <ul style="color: #92400e; margin-top: 0.5rem;">
                    <li><strong>This is a temporary approach</strong> to password handling for new account creation</li>
                    <li><strong>Keep your original password secure and private</strong> - never share it with anyone</li>
                    <li><strong>To create or update your trading sheet account:</strong>
                        <ol>
                            <li>Enter your desired password below</li>
                            <li>Press Enter to generate the encrypted hash</li>
                            <li>Share ONLY the encrypted hash with the EasyEquities DevOps </li>
                            <li>Inform the DevOps team whether this password is required for a new account, or whether you are simply updating your account password. For the former, you will need to provide your email address and follow formal onboarding SOPs.</li>
                        </ol>
                    </li>
                    <li>The EasyEquities DevOps team will use the encrypted hash to configure your account via a secure vault</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        # Password input for hash generation
        new_password = st.text_input(
            "Enter New Password",
            key="password_to_hash",
            type="password",
            placeholder="Password to encrypt for DevOps",
            help="Enter a password and press Enter to generate bcrypt hash"
        )
        
        # Generate hash when Enter is pressed or button clicked
        col1, col2 = st.columns(2)
        with col1:
            generate_button = st.button("🔐 Generate Hash", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.password_to_hash = ""
            if 'generated_hash' in st.session_state:
                del st.session_state['generated_hash']
            st.rerun()
        
        if (new_password and generate_button) or (new_password and 'password_to_hash' in st.session_state):
            try:
                # Generate bcrypt hash
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
                hash_string = hashed.decode('utf-8')
                st.session_state['generated_hash'] = hash_string
                
                # Display the hash in a styled container
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                            border: 2px solid #10b981; 
                            border-radius: 8px; 
                            padding: 1rem;">
                    <p style="margin: 0; color: #14532d; font-weight: 600;">✓ Encrypted Password Hash Generated:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display hash in a code block for easy copying
                st.code(hash_string, language="text")
                
                # Copy instructions
                st.markdown("""
                <div style="background: #f0f9ff; 
                            border-left: 4px solid #3b82f6; 
                            padding: 0.75rem; 
                            border-radius: 4px;
                            margin-top: 1rem;">
                    <p style="margin: 0; color: #1e3a8a; font-size: 0.9rem;">
                        <strong>📋 Next Steps:</strong><br/>
                        1. Copy the hash above (click to select all)<br/>
                        2. Send this hash to DevOps via secure channel<br/>
                        3. Keep your original password safe and private
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error generating hash: {str(e)}")
    
    # Stop execution here - don't show declaration form until authenticated
    st.stop()

# ============================================
# USER IS AUTHENTICATED - SHOW DECLARATION
# ============================================

# Get authenticated user info
current_user = get_current_user()
full_name = current_user['name']
email = current_user['email']

# Digital Signature Form
st.markdown("### Trader Information & Authorization")

# Show authenticated user info (read-only)
col1, col2 = st.columns(2)
with col1:
    st.text_input(
        "Full Name *",
        value=full_name,
        disabled=True,
        help="Authenticated user (from your account)"
    )

with col2:
    st.text_input(
        "Email Address *",
        value=email,
        disabled=True,
        help="Authenticated email (from your account)"
    )

# Declaration Checkboxes
st.markdown("### Trading Declarations")

consent_items = [
    ("data_accuracy", "I declare that all trading data provided is accurate, complete, and current"),
    ("authorization", "I am authorized to submit these trading instructions for execution"),
    ("compliance", "I confirm that all trades comply with applicable regulations and policies"),
    ("acceptance", "I accept that trades will be executed as submitted and cannot be reversed"),
    ("verification", "I have verified all trading parameters, amounts, and account information"),
    ("responsibility", "I accept full responsibility for the trading instructions submitted"),
    ("declaration", "I declare the information provided is timely and correct for processing")
]

# Accept All checkbox - removing all custom styling to eliminate empty divs
accept_all = persist_checkbox(
    "&#10003; **Accept All** - I agree to all declarations listed below", 
    "accept_all_consents",
    help="Check this to automatically accept all declaration items below"
)

# Handle Accept All functionality
if accept_all and not st.session_state.get('accept_all_processed', False):
    # User just checked "Accept All" - set all individual consents
    for key, _ in consent_items:
        st.session_state[key] = True
    st.session_state['accept_all_processed'] = True
    st.rerun()  # Refresh to show updated checkboxes
elif not accept_all and st.session_state.get('accept_all_processed', False):
    # User unchecked "Accept All" - clear all individual consents  
    for key, _ in consent_items:
        st.session_state[key] = False
    st.session_state['accept_all_processed'] = False
    st.rerun()  # Refresh to show updated checkboxes

# Individual declaration items
st.markdown("#### Individual Declaration Items")
for key, text in consent_items:
    persist_checkbox(text, key)

# Check if all consents are given (from session state, not widget return values)
all_consents_given = all(st.session_state.get(key, False) for key, _ in consent_items)

# Check if individual items match accept_all state
individual_all_checked = all(st.session_state.get(key, False) for key, _ in consent_items)
if individual_all_checked and not accept_all:
    st.session_state['accept_all_consents'] = True
    st.rerun()  # Refresh to show "Accept all" as checked
elif not individual_all_checked and accept_all and not st.session_state.get('accept_all_processed', False):
    st.session_state['accept_all_consents'] = False
    st.rerun()  # Refresh to show "Accept all" as unchecked

# Date and Time of Declaration
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Date of Declaration:** {current_date}")

# Proceed Button
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Show validation status to help users understand what's needed
if not full_name or not email or not all_consents_given:
    missing_items = []
    if not full_name:
        missing_items.append("Full Name")
    if not email:
        missing_items.append("Email Address")
    if not all_consents_given:
        missing_items.append("All trading declarations")
    
    st.warning(f"&#9888; Please complete the following to proceed: {', '.join(missing_items)}")

if full_name and email and all_consents_given:
    # Store consent information
    st.session_state.consent_given = True
    st.session_state.consent_name = full_name
    st.session_state.consent_email = email
    st.session_state.consent_date = current_date
    
    # Apply the same styling as main.py button but with red color - targeting specific element
    st.markdown("""
    <style>
    /* Target the specific button element */
    button.st-emotion-cache-saqyht.ef3psqc13,
    button[kind="primary"],
    .stButton > button,
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ed1847 0%, #c41230 100%) !important;
        color: white !important;
        padding: 0.875rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.0625rem !important;
        box-shadow: 0 4px 16px rgba(237, 24, 71, 0.3) !important;
        transition: all 0.3s ease !important;
        border: none !important;
        width: 100% !important;
        height: auto !important;
    }
    
    /* Hover effects */
    button.st-emotion-cache-saqyht.ef3psqc13:hover,
    button[kind="primary"]:hover,
    .stButton > button:hover,
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(237, 24, 71, 0.4) !important;
        background: linear-gradient(135deg, #c41230 0%, #a30f28 100%) !important;
    }
    
    /* Center the button */
    div[data-testid="column"]:has(button[kind="primary"]) {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("→ Proceed to Trading Sheet Upload", 
                    type="primary", 
                    use_container_width=True,
                    help="I declare all information is accurate and proceed to upload trading sheet"):
            # Show success message and navigate
            st.success("&#10003; Declaration recorded successfully!")
            st.balloons()
            st.switch_page('main.py')
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: #f3f4f6; border: 2px solid #9ca3af; border-radius: 12px; padding: 1.5rem; text-align: center;">
            <p style="margin: 0; color: #4b5563;"><strong>Please complete all required fields and declaration items above to proceed.</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 12px; text-align: center;">
    <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
        <strong>EasyEquities Trading Operations</strong><br>
        All trades are processed through the secure Accounts Processor API.<br>
        For support or questions, please contact: trading@easyequities.co.za
    </p>
</div>
""", unsafe_allow_html=True)
