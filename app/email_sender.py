"""
Email sending functionality for the Research Survey Application.

This module handles sending survey submissions via email with attachments.
"""

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
import datetime

def format_feedback_section(feedback_data: Dict[str, Any]) -> str:
    """Format feedback data for email inclusion."""
    section = "--- USER FEEDBACK ---\n"
    section += f"Survey: {feedback_data.get('survey_name', 'N/A')}\n"
    section += f"Email: {feedback_data.get('email', 'N/A')}\n"
    section += f"Category: {feedback_data.get('category', 'N/A')}\n"
    section += f"Satisfaction: {feedback_data.get('satisfaction_rating', 'N/A')}/5\n"
    section += f"Message: {feedback_data.get('message', 'N/A')}\n"
    section += "--- END FEEDBACK ---\n\n"
    return section

def send_submission_email(
    answers: Dict[str, Any],
    uploaded_files: List[Optional[st.runtime.uploaded_file_manager.UploadedFile]],
    feedback_data: Optional[Dict[str, Any]] = None
):
    """
    Send survey submission via email with PDF summary and any uploaded files.
    
    Args:
        answers: Complete survey submission data
        uploaded_files: List of uploaded documents (if any)
        feedback_data: Optional feedback data from user
    """
    
    try:
        # --- Credentials ---
        try:
            sender_email = st.secrets["email_credentials"]["email_address"]
            sender_password = st.secrets["email_credentials"]["app_password"]
        except KeyError as ke:
            st.error(f"Missing email credentials in secrets.toml: {ke}")
            st.error("Please configure email_credentials.email_address and email_credentials.app_password")
            return
        
        # --- Set the recipient email address ---
        # Default recipient email
        DEFAULT_RECIPIENT = "don.kruger123@gmail.com"
        
        # In dev mode, allow configurable email; otherwise use default
        if st.session_state.get("dev_mode", False):
            # Dev mode: Allow user to configure email or use default
            dev_email = st.session_state.get("dev_recipient_email", DEFAULT_RECIPIENT)
            recipient_email = dev_email
        else:
            # Production mode: Use default or from secrets if available
            try:
                recipient_email = st.secrets["email_credentials"].get("recipient_address", DEFAULT_RECIPIENT)
            except:
                recipient_email = DEFAULT_RECIPIENT

        # --- Extract Survey Information ---
        survey_type = answers.get("Survey Type", "Unknown Survey")
        
        # Extract informed consent signer name
        declaration_info = answers.get("Declaration", {})
        consent_signer = declaration_info.get("Informed Consent Signed By", "Anonymous")
        
        # --- Email Content ---
        subject = f"New Survey Submission: {survey_type}"

        body = f"A new survey has been submitted for review.\n\n"
        body += f"Survey Details:\n"
        body += f"• Survey Type: {survey_type}\n"
        body += f"• Informed Consent Signed By: {consent_signer}\n"
        body += f"• Submission Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        body += f"Please find the complete survey response attached as a PDF.\n"
        
        if uploaded_files and any(f is not None for f in uploaded_files):
            count = sum(1 for f in uploaded_files if f is not None)
            body += f"This submission includes {count} additional file(s).\n"
        
        # Add CSV note if available
        body += f"A CSV data file is also attached for data processing.\n\n"
        
        # Add feedback section if provided
        if feedback_data and feedback_data.get('submitted'):
            body += format_feedback_section(feedback_data)
        
        body += f"Regards,\n"
        body += f"Research Survey System"

        # --- Create the Email Message ---
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # --- Create standardized filenames ---
        safe_survey_name = survey_type.replace(' ', '_').replace('/', '_').replace('\\', '_')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"Survey_{safe_survey_name}_{timestamp}"

        # --- Attach PDF Summary ---
        try:
            from app.pdf_generator import make_pdf
            pdf_bytes = make_pdf(answers)
            pdf_part = MIMEBase("application", "octet-stream")
            pdf_part.set_payload(pdf_bytes)
            encoders.encode_base64(pdf_part)
            pdf_part.add_header(
                "Content-Disposition",
                f"attachment; filename={base_filename}.pdf",
            )
            msg.attach(pdf_part)
        except Exception as pdf_error:
            st.error(f"Could not generate PDF: {pdf_error}")
            # Continue without PDF

        # --- Attach CSV Data File ---
        try:
            # Check if this is an investment research survey
            if survey_type == "Investment Decision-Making Research Survey":
                from app.csv_generator import make_investment_research_csv
                csv_string = make_investment_research_csv(answers)
            else:
                from app.csv_generator import make_csv
                csv_string = make_csv(answers)
            
            csv_part = MIMEBase("application", "octet-stream")
            csv_part.set_payload(csv_string.encode("utf-8"))
            encoders.encode_base64(csv_part)
            csv_part.add_header(
                "Content-Disposition",
                f"attachment; filename={base_filename}.csv",
            )
            msg.attach(csv_part)
        except Exception as csv_error:
            # CSV generator might not be available
            pass

        # --- Attach User Uploaded Files ---
        if uploaded_files:
            for i, uploaded_file in enumerate(uploaded_files):
                if uploaded_file is not None:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(uploaded_file.getvalue())
                    encoders.encode_base64(part)
                    
                    # Use original filename or create a generic one
                    filename = uploaded_file.name or f"attachment_{i+1}"
                    
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={filename}",
                    )
                    msg.attach(part)

        # --- Send the Email ---
        st.info(f"Sending survey submission to: {recipient_email}")
        
        # Determine SMTP server from sender email
        if "gmail.com" in sender_email or "google" in sender_email.lower():
            smtp_server = "smtp.gmail.com"
        elif "outlook" in sender_email or "hotmail" in sender_email:
            smtp_server = "smtp-mail.outlook.com"
        elif "yahoo" in sender_email:
            smtp_server = "smtp.mail.yahoo.com"
        else:
            # Default to Gmail (can be overridden in secrets)
            smtp_server = st.secrets.get("email_credentials", {}).get("smtp_server", "smtp.gmail.com")
        
        with smtplib.SMTP_SSL(smtp_server, 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        st.success(f"Survey submission sent successfully!")
        st.info(f"Email sent to: {recipient_email}")
        st.info(f"Attachments: {base_filename}.pdf, {base_filename}.csv")
        
        if uploaded_files and any(f is not None for f in uploaded_files):
            count = sum(1 for f in uploaded_files if f is not None)
            st.info(f"Additional files: {count} file(s)")

    except Exception as e:
        st.error(f"Failed to send survey submission email: {e}")
        st.error("Please check your email configuration in .streamlit/secrets.toml and try again.")
        
        # Provide helpful configuration instructions
        with st.expander("Email Configuration Help"):
            st.markdown("""
            To configure email sending, create or update `.streamlit/secrets.toml`:
            
            ```toml
            [email_credentials]
            email_address = "your-email@gmail.com"
            app_password = "your-app-password"
            recipient_address = "don.kruger123@gmail.com"  # Optional, defaults to don.kruger123@gmail.com
            smtp_server = "smtp.gmail.com"  # Optional, auto-detected from sender email
            ```
            
            **For Gmail:**
            1. Enable 2-factor authentication
            2. Generate an app password at https://myaccount.google.com/apppasswords
            3. Use the app password (not your regular password) in the config
            """)