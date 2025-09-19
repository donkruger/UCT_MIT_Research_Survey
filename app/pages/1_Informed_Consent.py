"""
Informed Consent page for the AI-Driven Investment Advisory Research Study.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# --- PAGE CONFIG ---
favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.png"
st.set_page_config(
    page_title="Informed Consent - Research Study",
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.sidebar import render_sidebar
from app.styling import get_all_styles
from app.utils import initialize_state, persist_checkbox, persist_text_input

# Initialize and apply styling
initialize_state()
st.session_state.current_page = "consent"  # Set current page for progress tracking
st.markdown(get_all_styles(), unsafe_allow_html=True)
render_sidebar()

# Custom CSS for informed consent
st.markdown("""
<style>
.consent-header {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
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
    border-left: 4px solid #1e40af;
}

.consent-section h3 {
    color: #1e40af;
    margin-top: 0;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
}

.consent-icon {
    background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
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
    border: 2px solid #3b82f6;
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
    <h1 style="margin: 0 0 0.5rem 0; font-size: 2.25rem; color: white;">Research Study Participation</h1>
    <p style="margin: 0; font-size: 1.125rem; opacity: 0.95; color: white;">AI-Driven Investment Advisory System Evaluation</p>
</div>
""", unsafe_allow_html=True)

# Institution Information
st.markdown("""
<div class="institution-info">
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 1.25rem; font-weight: bold;">UCT</div>
        <div>
            <h3 style="margin: 0; color: #1e40af;">University of Cape Town</h3>
            <p style="margin: 0; color: #64748b;">School of Information Technology • Department of Information Systems</p>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
        <div>
            <strong>Researcher:</strong> Don Kruger<br>
            <strong>Phone:</strong> +27-84-555-3333<br>
            <strong>Email:</strong> don@easyequities.co.za
        </div>
        <div>
            <strong>Institution:</strong> Private Bag X3, Rondebosch 7701<br>
            <strong>Website:</strong> https://science.uct.ac.za/
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Invitation Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">i</span>Invitation to Participate</h3>
    <p>You are invited to participate in a research study conducted by the Department of Information Systems at the University of Cape Town. This study is part of a broader investigation into user experiences with AI-driven financial advisory systems.</p>
    <p><strong>Your participation will help us evaluate the usability, clarity, and effectiveness of a multi-agent investment advisory system.</strong> Stated differently, you will be interacting with a "team" of AI bots mandated to deliver you responsibly informed investment advice.</p>
    <p>We believe that your experience would be a valuable source of information, and hope that by participating you may gain useful knowledge.</p>
</div>
""", unsafe_allow_html=True)

# Procedures Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">•</span>Study Procedures</h3>
    <p>During this study, you will be asked to:</p>
    <ul>
        <li><strong>Cooperate with a multi-agent AI system</strong> through a chat-based interface</li>
        <li><strong>Complete a questionnaire</strong> which is expected to take 15-20 minutes to answer</li>
        <li><strong>Provide feedback</strong> on your experience with the AI-driven investment recommendations</li>
    </ul>
    <p>The entire process should take approximately 30-40 minutes of your time.</p>
</div>
""", unsafe_allow_html=True)

# Risks Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">!</span>Important Risks & Limitations</h3>
    <div class="risk-warning">
        <h4 style="color: #92400e; margin-top: 0;">⚠ Financial Risk Warning</h4>
        <p style="margin-bottom: 0;"><strong>The harmful risks to you, related to your participation in this study, may be your decision to financially act on the investment advice provided.</strong></p>
        <p style="margin-bottom: 0;"><strong>It is recommended that you appreciate the limitations of AI-driven insights and do not materially act on the investment advice provided.</strong></p>
    </div>
    <p><em>This is a research study only. The AI system is experimental and should not be used for actual investment decisions.</em></p>
</div>
""", unsafe_allow_html=True)

# Benefits Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">+</span>Potential Benefits</h3>
    <div class="benefits-box">
        <ul style="margin: 0;">
            <li>While there are no direct personal benefits to participation, your insights will contribute to the development of more transparent, user-friendly AI-driven financial advisory systems</li>
            <li>The study's findings may help improve AI-generated financial recommendations, making them more aligned with user expectations and ethical considerations</li>
            <li>You will gain exposure to cutting-edge AI technology in the financial advisory space</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# Confidentiality Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">◊</span>Confidentiality & Privacy</h3>
    <ul>
        <li><strong>All responses will be kept strictly confidential</strong> and will only be used for research purposes</li>
        <li><strong>No personally identifiable information</strong> will be collected, stored, or published</li>
        <li><strong>Data will be anonymized</strong> in all research outputs, ensuring that no individual responses can be linked back to participants</li>
        <li><strong>All information collected in this study will be kept private</strong> in that you will not be identified by name or by affiliation to an institution</li>
        <li><strong>Confidentiality and anonymity will be maintained</strong> throughout the research process</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Voluntary Participation Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">✓</span>Voluntary Participation</h3>
    <p><strong>Your participation is completely voluntary.</strong> You may:</p>
    <ul>
        <li>Refuse to participate without any consequences</li>
        <li>Withdraw at any time without having to state a reason</li>
        <li>Withdraw without any prejudice or penalty against you</li>
    </ul>
    <p><strong>Should you choose to withdraw,</strong> the researcher commits not to use any of the information you have provided without your signed consent. Note that the researcher may also withdraw you from the study at any time.</p>
</div>
""", unsafe_allow_html=True)

# Feedback Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">↵</span>Research Feedback</h3>
    <p>You will receive feedback about the results of this research by receiving a copy of the finalized research paper, in which your data is used in completely anonymized form.</p>
</div>
""", unsafe_allow_html=True)

# Questions Section
st.markdown("""
<div class="consent-section">
    <h3><span class="consent-icon">?</span>Questions & Further Information</h3>
    <ul>
        <li>If you have any questions or concerns before, during, or after the study, please feel free to contact the research team</li>
        <li>Additional information about the study can be provided upon request</li>
        <li><strong>Contact:</strong> Don Kruger at don@easyequities.co.za or +27-84-555-3333</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Consent Statement & Signature Section
st.markdown("""
<div class="signature-section">
    <h3 style="color: #0ea5e9; margin-top: 0; text-align: center;">✓ Consent Statement & Digital Signature</h3>
    <p style="text-align: center; margin-bottom: 2rem;"><em>By completing this section, you agree to participate in this research study.</em></p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
    <p><strong>The aim, procedures to be used, as well as the potential risks and benefits of your participation have been explained to you in detail using this form.</strong></p>
    <p>Refusal to participate in or withdrawal from this study at any time will have no effect on you in any way. You are free to contact the research team to ask questions or request further information at any time during this research.</p>
</div>
""", unsafe_allow_html=True)

# Digital Signature Form
st.markdown("### Digital Consent & Signature")

col1, col2 = st.columns(2)
with col1:
    full_name = persist_text_input(
        "Full Name *",
        "consent_full_name",
        placeholder="Enter your full legal name",
        help="This serves as your digital signature"
    )

with col2:
    email = persist_text_input(
        "Email Address *",
        "consent_email",
        placeholder="your.email@example.com",
        help="For research communication purposes only"
    )

# Consent Checkboxes
st.markdown("### Consent Confirmations")

consent_items = [
    ("understand_voluntary", "I understand that my participation is completely voluntary and that I can withdraw at any time"),
    ("understand_purpose", "The study's purpose and procedures have been fully explained to me"),
    ("understand_academic", "I understand this research is conducted for academic purposes only and does not provide immediate personal benefits"),
    ("understand_anonymous", "I understand my responses will be kept anonymous and used solely for research purposes"),
    ("understand_questions", "I understand I have the right to ask questions and receive clarification on any aspect of the study"),
    ("understand_risks", "I understand the risks associated with acting on AI-generated investment advice and will not make financial decisions based on this experimental system"),
    ("consent_participate", "I freely consent to take part in this research study")
]

# Accept All checkbox - removing all custom styling to eliminate empty divs
accept_all = persist_checkbox(
    "✓ **Accept All** - I agree to all consent items listed below", 
    "accept_all_consents",
    help="Check this to automatically accept all consent items below"
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

# Individual consent items
st.markdown("#### Individual Consent Items")
all_consents_given = True
for key, text in consent_items:
    consent_given = persist_checkbox(text, key)
    if not consent_given:
        all_consents_given = False

# Check if individual items match accept_all state
individual_all_checked = all(st.session_state.get(key, False) for key, _ in consent_items)
if individual_all_checked and not accept_all:
    st.session_state['accept_all_consents'] = True
    st.rerun()  # Refresh to show "Accept all" as checked
elif not individual_all_checked and accept_all and not st.session_state.get('accept_all_processed', False):
    st.session_state['accept_all_consents'] = False
    st.rerun()  # Refresh to show "Accept all" as unchecked

# Date and Final Consent
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Date of Consent:** {current_date}")

# Proceed Button
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

if full_name and email and all_consents_given:
    # Store consent information
    st.session_state.consent_given = True
    st.session_state.consent_name = full_name
    st.session_state.consent_email = email
    st.session_state.consent_date = current_date
    
    # Apply the same styling as main.py button but with custom color - targeting specific element
    st.markdown("""
    <style>
    /* Target the specific button element */
    button.st-emotion-cache-saqyht.ef3psqc13,
    button[kind="primary"],
    .stButton > button,
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1e3ea2 0%, #1a3491 100%) !important;
        color: white !important;
        padding: 0.875rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.0625rem !important;
        box-shadow: 0 4px 16px rgba(30, 62, 162, 0.3) !important;
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
        box-shadow: 0 6px 20px rgba(30, 62, 162, 0.4) !important;
        background: linear-gradient(135deg, #1a3491 0%, #162d80 100%) !important;
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
        if st.button("→ Begin AI Investment Advisory Study", 
                    type="primary", 
                    use_container_width=True,
                    help="I consent and want to begin the AI Investment Advisory Research Study"):
            # Show success message and navigate
            st.success("✓ Consent recorded successfully!")
            st.balloons()
            st.switch_page('main.py')
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: #f3f4f6; border: 2px solid #9ca3af; border-radius: 12px; padding: 1.5rem; text-align: center;">
            <p style="margin: 0; color: #4b5563;"><strong>Please complete all required fields and consent items above to proceed.</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 12px; text-align: center;">
    <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
        <strong>University of Cape Town - Department of Information Systems</strong><br>
        This research is conducted under the ethical guidelines of the University of Cape Town.<br>
        For any concerns about the research ethics, please contact the research team.
    </p>
</div>
""", unsafe_allow_html=True)
