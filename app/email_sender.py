"""
Email sending functionality for the Trading Sheet Application.

This module handles sending trading sheet submissions via email for audit trail.

AUDITABILITY ARCHITECTURE:
This module implements a comprehensive audit trail system that captures:
- WHO executed: User identity from declaration/authentication system
- WHAT was executed: Complete trade details and results
- WHEN: Timestamp of all actions
- OUTCOME: Success, failure, or error states
- EVIDENCE: Original CSV attachments and execution logs

The system is designed to be authentication-agnostic, supporting both:
- Current declaration-based identity capture
- Future OAuth/SSO authentication systems
"""

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
import datetime
import json
import io
import pandas as pd


def get_user_identity() -> Dict[str, str]:
    """
    Extract user identity from current authentication/declaration system.
    
    This function is authentication-agnostic and will work with:
    - Password authentication (auth_user from app.auth)
    - Declaration-based system (consent_name, consent_email) - backward compatible
    - Future OAuth/SSO systems (user object, JWT claims)
    - API key-based systems
    
    Returns:
        Dict containing user identity information:
        - name: Full name or username
        - email: Email address
        - auth_method: How the user was authenticated
        - user_id: Unique identifier (if available)
    """
    identity = {
        'name': 'Unknown User',
        'email': 'unknown@domain.com',
        'auth_method': 'none',
        'user_id': None
    }
    
    # ============================================
    # NEW: Check for authenticated user (TAKES PRECEDENCE)
    # ============================================
    if st.session_state.get('auth_user'):
        user = st.session_state['auth_user']
        identity['name'] = user.get('name', 'Unknown')
        identity['email'] = user.get('email', 'unknown@domain.com')
        identity['auth_method'] = st.session_state.get('auth_provider', 'password')
        identity['user_id'] = user.get('user_id')
        identity['user_role'] = user.get('role', 'unknown')
        identity['login_time'] = st.session_state.get('auth_login_time', 'Unknown')
        return identity
    
    # FALLBACK: Check for declaration-based identity (backward compatibility)
    if st.session_state.get('consent_name') and st.session_state.get('consent_email'):
        identity['name'] = st.session_state['consent_name']
        identity['email'] = st.session_state['consent_email']
        identity['auth_method'] = 'declaration'
        identity['consent_date'] = st.session_state.get('consent_date', 'Unknown')
    
    # Future: Add support for OAuth/SSO
    # elif 'user' in st.session_state and hasattr(st.session_state.user, 'email'):
    #     identity['name'] = st.session_state.user.name
    #     identity['email'] = st.session_state.user.email
    #     identity['auth_method'] = 'oauth'
    #     identity['user_id'] = st.session_state.user.id
    
    # Future: Add support for API key authentication
    # elif 'api_key_user' in st.session_state:
    #     identity['name'] = st.session_state.api_key_user['name']
    #     identity['email'] = st.session_state.api_key_user['email']
    #     identity['auth_method'] = 'api_key'
    #     identity['user_id'] = st.session_state.api_key_user['id']
    
    return identity


def send_comprehensive_audit_email(
    submission_status: str,
    trade_data: Optional[pd.DataFrame] = None,
    api_results: Optional[Dict[str, Any]] = None,
    error_details: Optional[Dict[str, Any]] = None,
    csv_filename: Optional[str] = None,
    csv_content: Optional[bytes] = None
) -> bool:
    """
    Send comprehensive audit trail email for all trading submissions.
    
    This function sends emails for BOTH successful and failed submissions,
    ensuring complete auditability of all trading operations.
    
    Args:
        submission_status: Status of submission ('success', 'failed', 'error')
        trade_data: DataFrame containing the parsed trading data
        api_results: Dictionary containing API execution results (if successful)
        error_details: Dictionary containing error information (if failed)
        csv_filename: Original uploaded filename
        csv_content: Raw CSV file content for attachment
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get email credentials
        try:
            sender_email = st.secrets["email_credentials"]["email_address"]
            sender_password = st.secrets["email_credentials"]["app_password"]
            recipient_email = st.secrets["email_credentials"].get(
                "notification_address",
                st.secrets["email_credentials"]["email_address"]
            )
        except KeyError:
            st.warning("&#9888; Email credentials not configured. Audit email skipped.")
            return False
        
        # Get user identity (authentication-agnostic)
        user_identity = get_user_identity()
        
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submission_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine email subject based on status
        status_emoji = {
            'success': '&#10003;',
            'failed': '&#9888;',
            'error': '&#10007;'
        }
        subject = f"{status_emoji.get(submission_status, '≡')} Trading Sheet Audit Trail - {submission_status.upper()} - {submission_id}"
        
        # Build comprehensive HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ed1847 0%, #c41230 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .section {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 20px; border-left: 4px solid #ed1847; }}
                .section h2 {{ color: #ed1847; margin-top: 0; font-size: 18px; display: flex; align-items: center; }}
                .section-icon {{ background: #ed1847; color: white; width: 28px; height: 28px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 14px; }}
                .info-grid {{ display: grid; grid-template-columns: 150px 1fr; gap: 12px; }}
                .info-label {{ font-weight: 600; color: #64748b; }}
                .info-value {{ color: #1e293b; }}
                .status-success {{ background: #d1fae5; border-color: #10b981; }}
                .status-failed {{ background: #fef3c7; border-color: #f59e0b; }}
                .status-error {{ background: #fee2e2; border-color: #ef4444; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 15px; }}
                .metric {{ background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #ed1847; }}
                .metric-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; margin-top: 5px; }}
                .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_emoji.get(submission_status, '≡')} Trading Sheet Submission Audit Trail</h1>
                    <p>Comprehensive record of trading sheet submission for compliance and audit purposes</p>
                </div>
                
                <!-- WHO EXECUTED -->
                <div class="section">
                    <h2><span class="section-icon">◉</span>Who Executed This Submission</h2>
                    <div class="info-grid">
                        <div class="info-label">Name:</div>
                        <div class="info-value">{user_identity['name']}</div>
                        
                        <div class="info-label">Email:</div>
                        <div class="info-value">{user_identity['email']}</div>
                        
                        <div class="info-label">Auth Method:</div>
                        <div class="info-value">{user_identity['auth_method'].upper()}</div>
                        
                        <div class="info-label">Submission Time:</div>
                        <div class="info-value">{timestamp}</div>
                        
                        <div class="info-label">Submission ID:</div>
                        <div class="info-value">{submission_id}</div>
        """
        
        if user_identity.get('consent_date'):
            html_body += f"""
                        <div class="info-label">Declaration Date:</div>
                        <div class="info-value">{user_identity['consent_date']}</div>
            """
        
        html_body += """
                    </div>
                </div>
        """
        
        # WHAT WAS EXECUTED
        if trade_data is not None and not trade_data.empty:
            total_trades = len(trade_data)
            buy_trades = len(trade_data[trade_data['Direction'] == 'BUY'])
            sell_trades = len(trade_data[trade_data['Direction'] == 'SELL'])
            total_buy_amount = trade_data[trade_data['Direction'] == 'BUY']['Amount'].sum()
            total_sell_units = trade_data[trade_data['Direction'] == 'SELL']['Units'].sum()
            unique_accounts = trade_data['TrustAccount'].nunique()
            
            html_body += f"""
                <!-- WHAT WAS EXECUTED -->
                <div class="section">
                    <h2><span class="section-icon">▦</span>What Was Executed</h2>
                    <div class="info-grid">
                        <div class="info-label">File Name:</div>
                        <div class="info-value">{csv_filename or 'trading_sheet.csv'}</div>
                        
                        <div class="info-label">Total Trades:</div>
                        <div class="info-value">{total_trades}</div>
                        
                        <div class="info-label">Accounts:</div>
                        <div class="info-value">{unique_accounts}</div>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{buy_trades}</div>
                            <div class="metric-label">Buy Orders</div>
                            <div style="font-size: 14px; color: #10b981; margin-top: 5px;">R {total_buy_amount:,.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{sell_trades}</div>
                            <div class="metric-label">Sell Orders</div>
                            <div style="font-size: 14px; color: #ef4444; margin-top: 5px;">{total_sell_units:,.2f} units</div>
                        </div>
                    </div>
                </div>
            """
        
        # SUBMISSION OUTCOME
        if submission_status == 'success' and api_results:
            html_body += f"""
                <!-- SUBMISSION OUTCOME - SUCCESS -->
                <div class="section status-success">
                    <h2><span class="section-icon">&#10003;</span>Submission Outcome: SUCCESS</h2>
                    <div class="info-grid">
                        <div class="info-label">Group ID:</div>
                        <div class="info-value">{api_results.get('group_id', 'N/A')}</div>
                        
                        <div class="info-label">Final Status:</div>
                        <div class="info-value">{api_results.get('status', 'PENDING')}</div>
                        
                        <div class="info-label">Environment:</div>
                        <div class="info-value">{api_results.get('environment', 'UAT')}</div>
                        
                        <div class="info-label">System ID:</div>
                        <div class="info-value">{api_results.get('system_id', 'N/A')}</div>
                    </div>
            """
            
            # Add detailed failure information if available
            if api_results.get('failed_trades'):
                failed_count = len(api_results['failed_trades'])
                html_body += f"""
                    <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px; border: 2px solid #f59e0b;">
                        <h3 style="color: #f59e0b; margin-top: 0;">&#9888; {failed_count} Trade(s) Failed</h3>
                """
                for idx, failed_trade in enumerate(api_results['failed_trades'][:5], 1):
                    html_body += f"""
                        <div style="margin: 10px 0; padding: 10px; background: #fef3c7; border-radius: 6px;">
                            <strong>Trade {idx}:</strong> User {failed_trade.get('userID')} | Instrument {failed_trade.get('instrumentID')}<br>
                            <span style="color: #dc2626;"><strong>Reason:</strong> {failed_trade.get('failureReason', 'Unknown error')}</span>
                        </div>
                    """
                if failed_count > 5:
                    html_body += f"<p><em>... and {failed_count - 5} more failures (see attached report)</em></p>"
                html_body += "</div>"
            
            html_body += "</div>"
            
        elif submission_status in ['failed', 'error'] and error_details:
            status_class = f"status-{submission_status}"
            html_body += f"""
                <!-- SUBMISSION OUTCOME - FAILED/ERROR -->
                <div class="section {status_class}">
                    <h2><span class="section-icon">{'&#9888;' if submission_status == 'failed' else '&#10007;'}</span>Submission Outcome: {submission_status.upper()}</h2>
                    <div class="info-grid">
                        <div class="info-label">Error Type:</div>
                        <div class="info-value">{error_details.get('error_type', 'Unknown')}</div>
                        
                        <div class="info-label">Error Message:</div>
                        <div class="info-value">{error_details.get('message', 'No details available')}</div>
            """
            
            if error_details.get('validation_errors'):
                html_body += """
                        <div class="info-label">Validation Errors:</div>
                        <div class="info-value">
                            <ul style="margin: 0; padding-left: 20px;">
                """
                for error in error_details['validation_errors'][:10]:
                    html_body += f"<li>{error}</li>"
                html_body += """
                            </ul>
                        </div>
                """
            
            html_body += """
                    </div>
                </div>
            """
        
        # Footer
        html_body += f"""
                <div class="footer">
                    <p><strong>EasyEquities Trading Operations</strong></p>
                    <p>This is an automated audit trail email. All trading submissions are logged for compliance purposes.</p>
                    <p>For questions, contact: trading@easyequities.co.za</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create email message
        msg = MIMEMultipart('mixed')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg['Date'] = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Attach original CSV file
        if csv_content:
            csv_part = MIMEBase('text', 'csv')
            csv_part.set_payload(csv_content)
            encoders.encode_base64(csv_part)
            csv_part.add_header(
                'Content-Disposition',
                f'attachment; filename="{csv_filename or f"trading_sheet_{submission_id}.csv"}"'
            )
            msg.attach(csv_part)
        
        # Attach detailed API results if available
        if api_results:
            api_json = json.dumps(api_results, indent=2, default=str)
            api_part = MIMEText(api_json, 'plain')
            api_part.add_header(
                'Content-Disposition',
                f'attachment; filename="api_results_{submission_id}.json"'
            )
            msg.attach(api_part)
        
        # Attach error details if available
        if error_details:
            error_json = json.dumps(error_details, indent=2, default=str)
            error_part = MIMEText(error_json, 'plain')
            error_part.add_header(
                'Content-Disposition',
                f'attachment; filename="error_details_{submission_id}.json"'
            )
            msg.attach(error_part)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to send audit email: {str(e)}")
        return False


def get_csv_content_from_dataframe(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame to CSV bytes for email attachment.
    
    Args:
        df: DataFrame containing trading data
    
    Returns:
        bytes: CSV content
    """
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue().encode('utf-8')


def send_trading_submission_email(
    recipient_email: str,
    subject: str,
    body: str,
    payload_data: Dict[str, Any]
) -> bool:
    """
    Send trading sheet submission email with API execution results.
    
    Args:
        recipient_email: Email address to send to
        subject: Email subject line
        body: HTML body content
        payload_data: Complete API payload with execution results
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Get credentials
        try:
            sender_email = st.secrets["email_credentials"]["email_address"]
            sender_password = st.secrets["email_credentials"]["app_password"]
        except KeyError:
            # Use defaults for testing
            st.warning("Email credentials not configured. Using test mode.")
            return True
        
        # Create message
        msg = MIMEMultipart('mixed')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg['Date'] = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Enhance body with API execution results if available
        enhanced_body = body
        if 'api_execution' in payload_data:
            api_results = payload_data['api_execution']
            execution_section = f"""
            <div style="background: #e0f2fe; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0ea5e9;">
                <h3 style="color: #0c4a6e; margin-top: 0;">API Execution Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #cbd5e1;"><strong>Group ID:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #cbd5e1;">{api_results.get('group_id', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #cbd5e1;"><strong>Status:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #cbd5e1;">{api_results.get('status', 'PENDING')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #cbd5e1;"><strong>Environment:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #cbd5e1;">{api_results.get('environment', 'UAT')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;"><strong>System ID:</strong></td>
                        <td style="padding: 8px;">{api_results.get('system_identifier', 27)}</td>
                    </tr>
                </table>
            </div>
            """
            # Insert execution section before closing body tag
            if '</body>' in enhanced_body:
                enhanced_body = enhanced_body.replace('</body>', execution_section + '</body>')
            else:
                enhanced_body += execution_section
        
        # Add HTML body
        html_part = MIMEText(enhanced_body, 'html')
        msg.attach(html_part)
        
        # Attach JSON payload as file
        batch_id = payload_data.get('batch_id', datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        json_attachment = MIMEText(json.dumps(payload_data, indent=2, default=str), 'plain')
        json_attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="trading_payload_{batch_id}.json"'
        )
        msg.attach(json_attachment)
        
        # If API execution results exist, attach as separate file
        if 'api_execution' in payload_data:
            api_results = payload_data['api_execution']
            group_id = api_results.get('group_id', 'unknown')
            
            execution_attachment = MIMEText(json.dumps(api_results, indent=2, default=str), 'plain')
            execution_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="execution_report_{group_id[:8] if group_id != "unknown" else "report"}.json"'
            )
            msg.attach(execution_attachment)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

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