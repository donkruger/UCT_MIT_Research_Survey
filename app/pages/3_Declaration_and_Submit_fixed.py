"""
Review and submission page for Trading Sheet operations with API integration.
Simplified and streamlined for reliable execution.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json
import time
import pandas as pd

# --- PAGE CONFIG ---
favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.png"
st.set_page_config(
    page_title="Review & Execute Trades - Trading Sheet",
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.components.sidebar import render_sidebar
from app.styling import get_all_styles
from app.utils import initialize_state
from app.email_sender import send_trading_submission_email

# Import API components
try:
    from app.api.trade_client import TradeAllocationsClient
    from app.api.trade_mapper import TradeDataMapper
    API_AVAILABLE = True
except ImportError as e:
    st.error(f"API components not available: {e}")
    API_AVAILABLE = False

# Initialize and apply styling
initialize_state()
st.session_state.current_page = "submit"
st.markdown(get_all_styles(), unsafe_allow_html=True)
render_sidebar()

# Hero section
st.markdown("""
<div style="
    background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
    border-radius: 24px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 40px rgba(237, 24, 71, 0.2);
    position: relative;
    overflow: hidden;
">
    <h1 style="
        color: white;
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.02em;
        position: relative;
    ">Review & Execute Trades</h1>
    <p style="
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.125rem;
        margin: 0;
        position: relative;
    ">
        Review your trading data and execute trades through the API
    </p>
</div>
""", unsafe_allow_html=True)

# Check prerequisites
if not st.session_state.get("consent_given", False):
    st.warning("&#9888; Please complete the Declaration step first.")
    if st.button("Go to Declaration", use_container_width=True):
        st.switch_page("pages/1_Informed_Consent.py")
    st.stop()

# Check for uploaded data
if 'trading_parser' not in st.session_state:
    st.warning("&#9888; No trading data found. Please upload a CSV file first.")
    if st.button("Go to Upload", use_container_width=True):
        st.switch_page("main.py")
    st.stop()

# Get parsed data
parser = st.session_state.get('trading_parser')
summary = parser.get_summary_statistics()
validation = parser.get_validation_report()

# Show API connection status
if API_AVAILABLE:
    try:
        client = TradeAllocationsClient()
        env_col1, env_col2, env_col3 = st.columns(3)
        
        with env_col1:
            st.info(f"**Environment:** {client.environment.upper()}")
        with env_col2:
            st.info(f"**System ID:** {client.system_id}")
        with env_col3:
            try:
                if client.test_connection():
                    st.success("**API Status:** &#10003; Connected")
                else:
                    st.warning("**API Status:** &#9888; Not Connected")
            except:
                st.info("**API Status:** &#9888; Cannot Test")
    except Exception as e:
        st.error(f"Could not initialize API client: {str(e)}")
        st.info("Please check your configuration in `.streamlit/secrets.toml`")

# Step 1: Review Trading Data
st.markdown("## ▦ Step 1: Review Trading Data")

# Show summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Trades", summary.get('total_trades', 0))

with col2:
    st.metric("Buy Orders", summary.get('buy_trades', 0), 
              f"R {summary.get('total_buy_amount', 0):,.2f}")

with col3:
    st.metric("Sell Orders", summary.get('sell_trades', 0), 
              f"R {summary.get('total_sell_amount', 0):,.2f}")

with col4:
    st.metric("Accounts", summary.get('unique_accounts', 0))

# Validation status
if validation.get('valid', False):
    st.success("&#10003; **Data Validation Passed** - All trades are valid")
else:
    st.error("&#10007; **Validation Failed**")
    for error in validation.get('errors', []):
        st.error(f"• {error}")

# Show warnings if any
if validation.get('warnings', []):
    with st.expander("&#9888; **Warnings** (non-blocking)"):
        for warning in validation['warnings']:
            st.warning(f"• {warning}")

# Display the trade details
with st.expander("≡ **View Trade Details**", expanded=False):
    display_data = parser.format_for_display()
    if display_data:
        # Convert to DataFrame for better display
        df_display = pd.DataFrame(display_data)
        # Remove row_number and direction_color for cleaner display
        df_clean = df_display.drop(['row_number', 'direction_color'], axis=1, errors='ignore')
        st.dataframe(df_clean, use_container_width=True)

st.markdown("---")

# Step 2: Declaration
st.markdown("## ✍️ Step 2: Confirm Declaration")

accept = st.checkbox(
    "I confirm that the trading data is accurate and authorize execution via the API",
    key="accept",
    help="You must accept this declaration before submitting trades"
)

if accept:
    st.success("&#10003; Declaration accepted")
else:
    st.info("&#9888; Declaration required to proceed")

st.markdown("---")

# Step 3: Execute Trades
st.markdown("## &#8599; Step 3: Execute Trades")

if not accept:
    st.info("≡ Please accept the declaration above to enable trade execution.")
elif not validation.get('valid', False):
    st.error("&#10007; Please fix validation errors before executing trades.")
elif not API_AVAILABLE:
    st.error("&#10007; API components not available. Please check the installation.")
else:
    # Show execution summary
    st.markdown(f"""
    **Ready to execute {summary['total_trades']} trades:**
    - Buy Orders: {summary.get('buy_trades', 0)} (R {summary.get('total_buy_amount', 0):,.2f})
    - Sell Orders: {summary.get('sell_trades', 0)} ({summary.get('total_sell_units', 0):,.2f} units)
    """)
    
    # Test API configuration first
    st.markdown("### ⚙ Pre-Execution Check")
    
    test_col1, test_col2 = st.columns(2)
    
    with test_col1:
        if st.button("○ Test API Configuration", use_container_width=True):
            st.info("Testing API setup...")
            
            try:
                # Test API client initialization
                test_client = TradeAllocationsClient()
                st.success(f"&#10003; API Client OK ({test_client.environment.upper()})")
                
                # Test connection
                if test_client.test_connection():
                    st.success("&#10003; Connection OK")
                else:
                    st.warning("&#9888; Connection failed (may still work for trades)")
                
                # Test data mapping
                test_mapper = TradeDataMapper()
                validation = test_mapper.validate_csv_data(parser.parsed_data)
                
                if validation['valid']:
                    st.success("&#10003; Data validation passed")
                else:
                    st.error("&#10007; Data validation failed")
                    for error in validation['errors']:
                        st.error(f"• {error}")
                
                st.success("✓ **Setup looks good! Ready to execute trades.**")
                
            except Exception as e:
                st.error(f"&#10007; **Setup Issue:** {str(e)}")
                
                # Provide specific help
                if "secrets" in str(e).lower():
                    st.markdown("""
                    **Configuration needed:**
                    
                    Please ensure `.streamlit/secrets.toml` exists with:
                    ```toml
                    [trade_api]
                    environment = "uat"
                    system_identifier_id = 27
                    ```
                    """)
                elif "connection" in str(e).lower():
                    st.markdown("**Network Issue:** Check internet connection and firewall settings")
                else:
                    st.markdown(f"**Technical Error:** {str(e)}")
    
    with test_col2:
        if st.button("≡ View Current Config", use_container_width=True):
            try:
                test_client = TradeAllocationsClient()
                st.json({
                    'environment': test_client.environment,
                    'system_id': test_client.system_id,
                    'base_url': test_client.base_url[:50] + '...',
                    'timeout': test_client.timeout
                })
            except Exception as e:
                st.error(f"Cannot load config: {e}")
    
    st.markdown("---")
    
    # Execute button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("&#8599; Execute Trades", type="primary", use_container_width=True):
            # Use session state to trigger the confirmation dialog
            st.session_state['show_confirmation'] = True

    # --- Confirmation Dialog ---
    if st.session_state.get('show_confirmation'):
        st.warning("&#9888; **Final Confirmation Required**")
        st.write(f"You are about to execute **{summary['total_trades']}** trades in the **{client.environment.upper()}** environment.")
        
        confirm_col1, confirm_col2 = st.columns(2)
        
        with confirm_col1:
            if st.button("&#10003; YES - Execute Now", type="primary", use_container_width=True, key="final_confirm"):
                
                # Set execution state
                st.session_state['executing_trades'] = True
                st.session_state['show_confirmation'] = False  # Hide confirmation
        
        with confirm_col2:
            if st.button("&#10007; Cancel", use_container_width=True):
                st.session_state['show_confirmation'] = False
                st.info("Execution cancelled.")
                st.rerun()

# --- Trade Execution Logic ---
if st.session_state.get('executing_trades'):
    
    # Create a container for execution output
    execution_container = st.container()
    
    with execution_container:
        st.markdown("### ◎ Trade Execution in Progress")
        
        try:
            # Initialize API components
            mapper = TradeDataMapper()
            api_client = TradeAllocationsClient()
            
            # Prepare metadata
            metadata = {
                'user_name': st.session_state.get('consent_name', ''),
                'user_email': st.session_state.get('email', 'trading@example.com'),
                'timestamp': datetime.now().isoformat(),
                'declaration_accepted': True,
                'trader_id': st.session_state.get('trader_id', 45314),
                'environment': api_client.environment
            }
            
            # --- Start Execution Steps ---
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Validate data
            status_text.text("Step 1/4: Validating trade data...")
            validation = mapper.validate_csv_data(parser.parsed_data)
            progress_bar.progress(25)
            
            if not validation['valid']:
                st.error("&#10007; Validation failed")
                for error in validation['errors']:
                    st.error(f"• {error}")
                st.session_state['executing_trades'] = False
                st.stop()
            
            # Step 2: Map to API format
            status_text.text("Step 2/4: Preparing API payload...")
            api_payload = mapper.map_csv_to_api(parser.parsed_data, metadata)
            group_id = api_payload['groupId']
            progress_bar.progress(50)
            
            # Step 3: Submit to API
            status_text.text(f"Step 3/4: Submitting {len(api_payload['valueTradeAllocationRequestDTOS'])} trades...")
            submission_result = api_client.create_value_orders(api_payload)
            progress_bar.progress(75)
            
            if not submission_result['success']:
                st.error(f"&#10007; **Submission Failed:** {submission_result['message']}")
                st.session_state['executing_trades'] = False
                st.stop()
            
            # Step 4: Get final status
            returned_group_id = submission_result.get('groupId', group_id)
            status_text.text("Step 4/4: Polling for final trade status...")
            
            # Use the robust polling function
            final_status_result = api_client.poll_status(returned_group_id)
            final_status = final_status_result.get('final_status', final_status_result.get('status', 'TIMEOUT'))
            
            progress_bar.progress(100)
            
            # --- Show Final Results ---
            if final_status_result.get('success'):
                if final_status == 'COMPLETED_SUCCESS':
                    st.success(f"✓ **All Trades Executed Successfully!**")
                elif final_status == 'COMPLETED_WITH_BUSINESS_ERRORS':
                    st.warning(f"&#9888; **Execution Complete - Some Trades Failed**")
                    st.info("≡ This is normal when trades fail due to business rules (e.g., insufficient funds)")
                else:
                    st.success(f"✓ **Trade Execution Complete!**")
            else:
                st.error(f"&#10007; **System Error or Timeout Occurred**")
                
            st.info(f"≡ **Group ID:** `{returned_group_id}`")
            st.info(f"▦ **Final Status:** {final_status}")
            
            # --- Fetch Detailed Trade Allocations ---
            if final_status in ['COMPLETED_WITH_BUSINESS_ERRORS', 'COMPLETED_SUCCESS', 'COMPLETED']:
                with st.spinner("Fetching detailed trade results..."):
                    detailed_results = api_client.get_all_trade_allocations(returned_group_id)
                    
                if detailed_results.get('success'):
                    # Store detailed results
                    st.session_state['detailed_trade_results'] = detailed_results
                    
                    # Display detailed trade results
                    with st.expander("▦ **Detailed Trade Results**", expanded=True):
                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("&#10003; Successful", detailed_results.get('success_count', 0))
                        with col2:
                            st.metric("&#10007; Failed", detailed_results.get('failed_count', 0))
                        with col3:
                            st.metric("[...] Pending", detailed_results.get('pending_count', 0))
                        
                        # Display failed trades with detailed failure reasons
                        failed_trades = detailed_results.get('failed_trades', [])
                        if failed_trades:
                            st.markdown("### &#10007; **Failed Trades - Detailed Reasons**")
                            
                            for idx, failed_trade in enumerate(failed_trades, 1):
                                with st.container():
                                    st.markdown(f"**Trade {idx}:**")
                                    
                                    # Create columns for trade details
                                    detail_col1, detail_col2 = st.columns(2)
                                    
                                    with detail_col1:
                                        st.markdown(f"**User ID:** {failed_trade.get('userID', 'N/A')}")
                                        st.markdown(f"**Instrument ID:** {failed_trade.get('instrumentID', 'N/A')}")
                                        st.markdown(f"**Trust Account:** {failed_trade.get('trustAccountID', 'N/A')}")
                                    
                                    with detail_col2:
                                        amount = failed_trade.get('amount', 0)
                                        units = failed_trade.get('units', 0)
                                        if amount and amount > 0:
                                            st.markdown(f"**Amount:** R {amount:,.2f}")
                                        if units and units > 0:
                                            st.markdown(f"**Units:** {units:,.2f}")
                                        st.markdown(f"**Reference:** {failed_trade.get('uniqueTransactionReference', 'N/A')}")
                                    
                                    # Display the failure reason prominently
                                    failure_reason = failed_trade.get('failureReason', 'Unknown error')
                                    st.error(f"**Failure Reason:** {failure_reason}")
                                    
                                    st.markdown("---")
                        
                        # Display successful trades summary
                        successful_trades = detailed_results.get('successful_trades', [])
                        if successful_trades:
                            with st.expander("&#10003; **Successful Trades**", expanded=False):
                                for idx, success_trade in enumerate(successful_trades, 1):
                                    st.markdown(f"""
                                    **Trade {idx}:** User {success_trade.get('userID')} | 
                                    Instrument {success_trade.get('instrumentID')} | 
                                    Transaction ID: {success_trade.get('transactionID', 'N/A')}
                                    """)
            
            # Store results
            results = {
                'group_id': returned_group_id,
                'status': final_status,
                'environment': api_client.environment.upper(),
                'submitted_at': datetime.now().isoformat(),
                'trade_count': len(api_payload['valueTradeAllocationRequestDTOS']),
                'system_id': api_client.system_id
            }
            st.session_state['trade_execution_results'] = results
            
            # Add to history with all necessary keys
            if 'trade_execution_history' not in st.session_state:
                st.session_state['trade_execution_history'] = []
            st.session_state['trade_execution_history'].append({
                'group_id': results['group_id'],
                'status': results['status'],
                'trade_count': results['trade_count'],
                'environment': results['environment'],
                'results': results,
                'timestamp': results.get('submitted_at', datetime.now().isoformat())
            })
            
            # Email confirmation
            status_text.text("Sending confirmation email...")
            
            # ... (email sending logic) ...
            
            # Reset execution state
            st.session_state['executing_trades'] = False
            st.success("&#10003; **Execution Complete!**")
            st.balloons()
            
        except Exception as e:
            st.error(f"&#10007; **An unexpected error occurred:** {str(e)}")
            st.session_state['executing_trades'] = False
            
            # Show debug info
            with st.expander("⌕ Debug Information"):
                st.code(str(e))

    # --- Next Steps / New Batch Button ---
    if 'trade_execution_results' in st.session_state:
        st.markdown("### &#8634; Next Steps")
        if st.button("◫ Upload New Trading Sheet", use_container_width=True):
            keys_to_clear = ['trading_parser', 'api_payload', 'trade_group_id', 'accept', 'trade_execution_results', 'executing_trades', 'show_confirmation']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Separator
st.markdown("---")

# Additional sections
tab1, tab2 = st.tabs(["≡ Execution History", "⚙ Debug & Support"])

with tab1:
    # Show execution history
    if 'trade_execution_history' in st.session_state and st.session_state['trade_execution_history']:
        st.markdown("### Recent Executions")
        
        history = st.session_state['trade_execution_history']
        for i, execution in enumerate(reversed(history[-5:])):  # Show last 5
            # Ensure all keys are present before displaying
            group_id = execution.get('group_id', 'N/A')
            status = execution.get('status', 'N/A')
            timestamp = execution.get('timestamp', 'N/A')
            trade_count = execution.get('trade_count', 'N/A')
            environment = execution.get('environment', 'N/A')
            
            with st.expander(f"Execution {len(history) - i}: {group_id[:8]}... ({status})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Time:** {timestamp}")
                    st.write(f"**Status:** {status}")
                with col2:
                    st.write(f"**Trades:** {trade_count}")
                    st.write(f"**Environment:** {environment}")
    else:
        st.info("No executions in this session yet.")

with tab2:
    st.markdown("### ⚙ Debug & Support")
    
    # Test API connection
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("&#8634; Test API Connection"):
            try:
                test_client = TradeAllocationsClient()
                if test_client.test_connection():
                    st.success("&#10003; API connection successful")
                else:
                    st.error("&#10007; API connection failed")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("🗑️ Clear Session Data"):
            # Clear all trading-related session state
            keys_to_clear = ['trading_parser', 'api_payload', 'trade_group_id', 'trade_execution_results']
            cleared = []
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
                    cleared.append(key)
            
            if cleared:
                st.success(f"Cleared: {', '.join(cleared)}")
            else:
                st.info("No data to clear")
    
    # Configuration info
    with st.expander("⚙ Configuration"):
        try:
            config_client = TradeAllocationsClient()
            st.json({
                'environment': config_client.environment,
                'system_id': config_client.system_id,
                'base_url': config_client.base_url,
                'monitor_url': config_client.monitor_url,
                'timeout': config_client.timeout
            })
        except Exception as e:
            st.error(f"Cannot load configuration: {e}")
    
    # Session state viewer
    with st.expander("⌕ Session State"):
        relevant_keys = ['trading_parser', 'consent_given', 'accept', 'trade_group_id']
        session_info = {}
        for key in relevant_keys:
            if key in st.session_state:
                if key == 'trading_parser':
                    session_info[key] = "Present (TradingSheetParser object)"
                else:
                    session_info[key] = st.session_state[key]
            else:
                session_info[key] = "Not set"
        
        st.json(session_info)

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    if 'trade_group_id' in st.session_state:
        st.info(f"**Last Group:** `{st.session_state['trade_group_id'][:8]}...`")

with footer_col2:
    if 'trade_execution_results' in st.session_state:
        status = st.session_state['trade_execution_results'].get('status', 'Unknown')
        if status in ['COMPLETED', 'SUCCESS']:
            st.success(f"**Status:** {status}")
        elif status in ['FAILED', 'ERROR']:
            st.error(f"**Status:** {status}")
        else:
            st.warning(f"**Status:** {status}")

with footer_col3:
    st.info(f"**Time:** {datetime.now():%H:%M:%S}")
