"""
Enhanced trade execution component with comprehensive UI/UX.
Provides complete workflow from CSV upload review to trade execution and confirmation.
"""

import streamlit as st
from typing import Dict, Any, Optional, Tuple
import pandas as pd
from datetime import datetime
import json
import time

from app.api.trade_client import TradeAllocationsClient
from app.api.trade_mapper import TradeDataMapper
from app.components.trade_status import render_trade_status, render_status_summary

def render_trade_review(parser_data: Dict[str, Any]) -> bool:
    """
    Render the trade review interface with detailed information.
    
    Args:
        parser_data: Parsed trading data from CSV
        
    Returns:
        Boolean indicating if user wants to proceed
    """
    
    # Extract data
    parsed_df = parser_data.get('data')
    summary = parser_data.get('summary', {})
    validation = parser_data.get('validation', {})
    
    # Header with summary metrics
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #0ea5e9;
    ">
        <h3 style="margin: 0 0 1rem 0; color: #0c4a6e;">▦ Trading Data Summary</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Trades",
            value=summary.get('total_trades', 0),
            help="Total number of trade orders to execute"
        )
    
    with col2:
        buy_count = summary.get('buy_trades', 0)
        st.metric(
            label="Buy Orders",
            value=buy_count,
            delta=f"R {summary.get('total_buy_amount', 0):,.2f}",
            delta_color="normal"
        )
    
    with col3:
        sell_count = summary.get('sell_trades', 0)
        st.metric(
            label="Sell Orders",
            value=sell_count,
            delta=f"R {summary.get('total_sell_amount', 0):,.2f}",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Unique Accounts",
            value=summary.get('unique_accounts', 0),
            help="Number of unique trust accounts"
        )
    
    # Validation Status
    if validation.get('valid', False):
        st.success("&#10003; **Data Validation Passed** - All trades are valid and ready for submission")
    else:
        st.error("&#10007; **Validation Failed** - Please fix the errors below before proceeding")
        for error in validation.get('errors', []):
            st.error(f"• {error}")
        return False
    
    # Show warnings if any
    if validation.get('warnings', []):
        with st.warning("&#9888; **Warnings** - Review these items (non-blocking)"):
            for warning in validation['warnings']:
                st.write(f"• {warning}")
    
    # Display the trade details
    with st.expander("≡ **View Trade Details**", expanded=True):
        # Create a formatted display dataframe
        display_df = parsed_df.copy()
        
        # Format numeric columns for display
        display_df['Amount'] = display_df['Amount'].apply(lambda x: f"R {x:,.2f}")
        display_df['Units'] = display_df['Units'].apply(lambda x: f"{x:.4f}")
        
        # Add color coding for Direction
        def color_direction(val):
            if val == 'BUY':
                return 'background-color: #dcfce7; color: #166534;'
            elif val == 'SELL':
                return 'background-color: #fee2e2; color: #991b1b;'
            return ''
        
        # Apply styling
        styled_df = display_df.style.applymap(color_direction, subset=['Direction'])
        st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Share distribution visualization
    if summary.get('trades_by_share'):
        st.subheader("&#8599; Trade Distribution by Share Code")
        share_data = pd.DataFrame(
            list(summary['trades_by_share'].items()),
            columns=['Share Code', 'Count']
        )
        st.bar_chart(share_data.set_index('Share Code'))
    
    return True

def render_pre_execution_checks(api_client: TradeAllocationsClient) -> Tuple[bool, Dict[str, Any]]:
    """
    Perform and display pre-execution checks.
    
    Returns:
        Tuple of (can_proceed, check_results)
    """
    
    st.subheader("⌕ Pre-Execution Checks")
    
    checks = {
        'api_connection': {'status': 'checking', 'message': 'Checking API connection...'},
        'environment': {'status': 'checking', 'message': 'Verifying environment...'},
        'credentials': {'status': 'checking', 'message': 'Validating credentials...'},
        'system_id': {'status': 'checking', 'message': 'Confirming system identifier...'}
    }
    
    # Create placeholder for dynamic updates
    check_placeholder = st.empty()
    
    def update_checks_display():
        """Update the checks display."""
        html = '<div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">'
        
        for check_name, check_data in checks.items():
            status = check_data['status']
            message = check_data['message']
            
            if status == 'success':
                icon = '&#10003;'
                color = '#10b981'
            elif status == 'error':
                icon = '&#10007;'
                color = '#ef4444'
            elif status == 'warning':
                icon = '&#9888;'
                color = '#f59e0b'
            else:
                icon = '[...]'
                color = '#6b7280'
            
            html += f'''
            <div style="display: flex; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                <span style="font-size: 1.25rem; margin-right: 0.75rem;">{icon}</span>
                <span style="flex: 1; color: #374151;">{message}</span>
            </div>
            '''
        
        html += '</div>'
        check_placeholder.markdown(html, unsafe_allow_html=True)
    
    # Perform checks
    update_checks_display()
    time.sleep(0.5)  # Visual effect
    
    # Check 1: API Connection
    if api_client.test_connection():
        checks['api_connection'] = {
            'status': 'success',
            'message': 'API connection established'
        }
    else:
        checks['api_connection'] = {
            'status': 'error',
            'message': 'Cannot connect to API - check network and configuration'
        }
    update_checks_display()
    
    # Check 2: Environment
    checks['environment'] = {
        'status': 'success' if api_client.environment in ['uat', 'qa', 'prod'] else 'warning',
        'message': f'Environment: {api_client.environment.upper()}'
    }
    update_checks_display()
    
    # Check 3: Credentials
    has_auth = 'api_key' in api_client.config or api_client.environment == 'uat'
    checks['credentials'] = {
        'status': 'success' if has_auth else 'warning',
        'message': 'Authentication configured' if has_auth else 'No authentication configured (may be required)'
    }
    update_checks_display()
    
    # Check 4: System ID
    checks['system_id'] = {
        'status': 'success',
        'message': f'System Identifier: {api_client.system_id}'
    }
    update_checks_display()
    
    # Determine if can proceed
    can_proceed = all(
        check['status'] != 'error' 
        for check in checks.values()
    )
    
    if can_proceed:
        st.success("&#10003; All pre-execution checks passed")
    else:
        st.error("&#10007; Pre-execution checks failed - please resolve issues above")
    
    return can_proceed, checks

def execute_trades_with_ui(
    parsed_data: pd.DataFrame,
    metadata: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Execute trades with comprehensive UI feedback.
    
    Args:
        parsed_data: Parsed trading DataFrame
        metadata: Additional metadata
        
    Returns:
        Tuple of (success, results)
    """
    
    # Initialize components
    mapper = TradeDataMapper()
    api_client = TradeAllocationsClient()
    
    # Validation phase
    st.markdown("### ◎ Trade Execution Process")
    
    # Step 1: Validate data
    with st.spinner("Validating trade data..."):
        validation = mapper.validate_csv_data(parsed_data)
        
        if not validation['valid']:
            st.error("&#10007; Validation failed:")
            for error in validation['errors']:
                st.error(f"• {error}")
            
            # Show troubleshooting tips
            with st.expander("⚙ Troubleshooting Tips"):
                st.markdown("""
                **Common validation issues:**
                - Ensure Direction is exactly 'BUY' or 'SELL' (case-sensitive)
                - Check that all Amount values are positive numbers
                - Verify UserID and TrustAccount are valid integers
                - Confirm InstrumentID matches valid instruments
                """)
            
            return False, None
    
    # Step 2: Pre-execution checks
    can_proceed, check_results = render_pre_execution_checks(api_client)
    if not can_proceed:
        return False, None
    
    # Step 3: Map data to API format
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Preparing trade data...")
    progress_bar.progress(25)
    
    try:
        api_payload = mapper.map_csv_to_api(parsed_data, metadata)
        st.session_state['api_payload'] = api_payload
        
        # Show payload preview
        with st.expander("⌕ API Payload Preview (Technical Details)", expanded=False):
            # Show summary instead of full payload
            st.json({
                'systemIdentifierID': api_payload['systemIdentifierID'],
                'groupId': api_payload['groupId'],
                'trade_count': len(api_payload['valueTradeAllocationRequestDTOS']),
                'first_trade': api_payload['valueTradeAllocationRequestDTOS'][0] if api_payload['valueTradeAllocationRequestDTOS'] else None
            })
    except Exception as e:
        st.error(f"&#10007; Failed to prepare trade data: {str(e)}")
        return False, None
    
    # Step 4: Submit to API
    status_text.text(f"Submitting {len(api_payload['valueTradeAllocationRequestDTOS'])} trades to {api_client.environment.upper()}...")
    progress_bar.progress(50)
    
    submission_result = api_client.create_value_orders(api_payload)
    
    if not submission_result['success']:
        progress_bar.progress(100)
        status_text.empty()
        
        # Show detailed error information
        st.error(f"&#10007; **Trade Submission Failed**")
        st.error(submission_result['message'])
        
        # Show troubleshooting tips
        if 'troubleshooting' in submission_result:
            with st.expander("⚙ Troubleshooting Suggestions", expanded=True):
                for tip in submission_result['troubleshooting']:
                    st.write(f"• {tip}")
        
        # Show technical details for debugging
        with st.expander("≡ Technical Details (for support)"):
            st.json({
                'endpoint': submission_result.get('endpoint'),
                'status_code': submission_result.get('status_code'),
                'error': submission_result.get('error'),
                'timestamp': datetime.now().isoformat()
            })
        
        # Offer to download the payload for manual review
        st.download_button(
            label="💾 Download API Payload for Review",
            data=json.dumps(api_payload, indent=2),
            file_name=f"failed_trade_payload_{datetime.now():%Y%m%d_%H%M%S}.json",
            mime="application/json",
            help="Download the payload to share with technical support"
        )
        
        return False, submission_result
    
    # Step 5: Monitor execution
    status_text.text("Trade orders submitted successfully. Monitoring execution...")
    progress_bar.progress(75)
    
    group_id = submission_result.get('groupId')
    st.success(f"&#10003; **Orders Submitted Successfully**")
    st.info(f"≡ Group ID: `{group_id}`")
    
    # Store for tracking
    st.session_state['trade_group_id'] = group_id
    
    # Step 6: Real-time status monitoring
    progress_bar.progress(90)
    status_text.text("Monitoring trade execution status...")
    
    # Use the enhanced status monitoring component
    final_status = render_trade_status(group_id, api_client)
    
    # Step 7: Format results
    progress_bar.progress(100)
    status_text.empty()
    progress_bar.empty()
    
    # Format the complete results
    api_results = mapper.format_api_response(final_status)
    api_results['submission_result'] = submission_result
    
    # Store complete results
    st.session_state['trade_execution_results'] = api_results
    
    # Show execution summary
    render_status_summary(api_results)
    
    # Offer download options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="← Download Execution Report",
            data=json.dumps(api_results, indent=2),
            file_name=f"execution_report_{group_id[:8]}_{datetime.now():%Y%m%d_%H%M%S}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Create a summary CSV
        summary_df = pd.DataFrame([{
            'Group ID': group_id,
            'Status': api_results.get('status'),
            'Environment': api_results.get('environment'),
            'Total Trades': api_results.get('trade_count'),
            'Timestamp': api_results.get('submitted_at')
        }])
        
        st.download_button(
            label="▦ Download Summary CSV",
            data=summary_df.to_csv(index=False),
            file_name=f"trade_summary_{group_id[:8]}_{datetime.now():%Y%m%d_%H%M%S}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        st.download_button(
            label="💾 Download API Payload",
            data=json.dumps(api_payload, indent=2),
            file_name=f"api_payload_{group_id[:8]}_{datetime.now():%Y%m%d_%H%M%S}.json",
            mime="application/json",
            use_container_width=True
        )
    
    return True, api_results

def render_troubleshooting_panel():
    """
    Render a troubleshooting panel with common issues and solutions.
    """
    
    with st.expander("⚙ **Troubleshooting Guide**", expanded=False):
        st.markdown("""
        ### Common Issues and Solutions
        
        #### 1. CSV Format Issues
        - **Problem:** "Missing required columns" error
        - **Solution:** Ensure your CSV has all required columns: ShareCode, ContractCode, InstrumentID, Units, Amount, Direction, UserID, TrustAccount
        
        #### 2. Validation Errors
        - **Problem:** "Invalid Direction values" error
        - **Solution:** Direction must be exactly 'BUY' or 'SELL' (case-sensitive)
        
        #### 3. API Connection Issues
        - **Problem:** Cannot connect to API
        - **Solutions:**
          - Check your internet connection
          - Verify API URLs in `.streamlit/secrets.toml`
          - Ensure firewall allows HTTPS connections
        
        #### 4. Authentication Failures
        - **Problem:** 401 or 403 errors
        - **Solutions:**
          - Verify API credentials if required
          - Check system identifier is set to 27
          - Confirm environment access permissions
        
        #### 5. Trade Execution Failures
        - **Problem:** Trades fail during execution
        - **Solutions:**
          - Verify UserID exists in the system
          - Check InstrumentID is valid for trading
          - Ensure TrustAccount has sufficient balance
          - Confirm trading hours if applicable
        
        ### Debug Information
        """)
        
        # Show last API request/response if available
        if 'last_api_request' in st.session_state:
            st.subheader("Last API Request")
            st.json(st.session_state['last_api_request'])
        
        if 'last_api_response' in st.session_state:
            st.subheader("Last API Response")
            st.json(st.session_state['last_api_response'])
        
        # Environment details
        st.subheader("Environment Configuration")
        try:
            client = TradeAllocationsClient()
            st.json({
                'environment': client.environment,
                'base_url': client.base_url,
                'monitor_url': client.monitor_url,
                'system_id': client.system_id,
                'timeout': client.timeout
            })
        except Exception as e:
            st.error(f"Could not load configuration: {str(e)}")
        
        # Support contact
        st.markdown("""
        ### Need Help?
        
        ✉ **Technical Support:** api-support@easyequities.io
        📚 **Documentation:** Check the API Integration Blueprint
        ⌕ **Logs:** Check application logs for detailed error messages
        """)

def render_execution_history():
    """
    Display execution history from the current session.
    """
    
    if 'trade_execution_history' not in st.session_state:
        st.session_state['trade_execution_history'] = []
    
    history = st.session_state['trade_execution_history']
    
    if not history:
        st.info("No trade executions in this session yet.")
        return
    
    st.subheader(f"≡ Execution History ({len(history)} batches)")
    
    # Create a summary table
    history_data = []
    for execution in history:
        history_data.append({
            'Time': execution['timestamp'],
            'Group ID': execution['group_id'][:8] + '...',
            'Status': execution['status'],
            'Trades': execution['trade_count'],
            'Environment': execution['environment']
        })
    
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)
    
    # Offer to download complete history
    if st.button("← Download Complete History"):
        st.download_button(
            label="Download JSON",
            data=json.dumps(history, indent=2),
            file_name=f"execution_history_{datetime.now():%Y%m%d_%H%M%S}.json",
            mime="application/json"
        )
