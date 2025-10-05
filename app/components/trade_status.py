"""
Real-time trade status monitoring component.
Provides visual feedback for trade execution progress and results.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import time
from datetime import datetime
import json

def render_trade_status(group_id: str, api_client) -> Dict[str, Any]:
    """
    Render real-time trade status with polling and visual feedback.
    
    Args:
        group_id: Trade group identifier
        api_client: Initialized TradeAllocationsClient
        
    Returns:
        Final status data with execution results
    """
    
    # Create placeholders for dynamic updates
    status_placeholder = st.empty()
    details_placeholder = st.empty()
    metrics_placeholder = st.empty()
    
    # Status color and icon mapping
    status_config = {
        'PENDING': {'color': '#f59e0b', 'icon': '[...]', 'label': 'Pending'},
        'PROCESSING': {'color': '#3b82f6', 'icon': '⚙', 'label': 'Processing'},
        'COMPLETED': {'color': '#10b981', 'icon': '&#10003;', 'label': 'Completed'},
        'SUCCESS': {'color': '#10b981', 'icon': '&#10003;', 'label': 'Success'},
        'FAILED': {'color': '#ef4444', 'icon': '&#10007;', 'label': 'Failed'},
        'PARTIAL': {'color': '#8b5cf6', 'icon': '&#9888;', 'label': 'Partial Success'},
        'TIMEOUT': {'color': '#6b7280', 'icon': '◷', 'label': 'Timeout'},
        'ERROR': {'color': '#ef4444', 'icon': '&#9888;', 'label': 'Error'},
        'UNKNOWN': {'color': '#6b7280', 'icon': '?', 'label': 'Unknown'}
    }
    
    def update_status_display(status_data: Dict[str, Any], elapsed_time: float):
        """Update the status display with current data."""
        status = status_data.get('status', 'UNKNOWN').upper()
        config = status_config.get(status, status_config['UNKNOWN'])
        
        status_html = f"""
        <div style="
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            border: 2px solid {config['color']}20;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="margin: 0 0 0.5rem 0; color: #1f2937; display: flex; align-items: center;">
                        <span style="font-size: 1.5rem; margin-right: 0.5rem;">{config['icon']}</span>
                        Trade Execution Status
                    </h3>
                    <p style="margin: 0; color: #6b7280; font-size: 0.875rem;">
                        Group ID: <code style="background: #f3f4f6; padding: 2px 6px; border-radius: 4px;">
                        {group_id[:8]}...{group_id[-4:]}
                        </code>
                    </p>
                    <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.75rem;">
                        Elapsed: {elapsed_time:.1f}s | Environment: {api_client.environment.upper()}
                    </p>
                </div>
                <div style="
                    background: {config['color']}20;
                    color: {config['color']};
                    padding: 0.75rem 1.25rem;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 1rem;
                    border: 2px solid {config['color']}40;
                ">
                    {config['label']}
                </div>
            </div>
            
            {render_progress_bar(status, elapsed_time)}
        </div>
        """
        
        status_placeholder.markdown(status_html, unsafe_allow_html=True)
    
    def render_progress_bar(status: str, elapsed_time: float) -> str:
        """Render animated progress bar based on status."""
        
        # Calculate progress percentage
        if status == 'PENDING':
            progress = min(0.25 + (elapsed_time / 100), 0.3)  # Slowly increase up to 30%
        elif status == 'PROCESSING':
            progress = min(0.5 + (elapsed_time / 200), 0.8)  # Increase up to 80%
        elif status in ['COMPLETED', 'SUCCESS', 'FAILED']:
            progress = 1.0
        else:
            progress = 0.5
        
        # Animated stripes for processing state
        animation = """
            @keyframes progress-stripes {
                0% { background-position: 40px 0; }
                100% { background-position: 0 0; }
            }
        """ if status == 'PROCESSING' else ""
        
        stripe_style = """
            background-image: linear-gradient(
                45deg,
                rgba(255, 255, 255, 0.15) 25%,
                transparent 25%,
                transparent 50%,
                rgba(255, 255, 255, 0.15) 50%,
                rgba(255, 255, 255, 0.15) 75%,
                transparent 75%,
                transparent
            );
            background-size: 40px 40px;
            animation: progress-stripes 1s linear infinite;
        """ if status == 'PROCESSING' else ""
        
        return f"""
        <style>{animation}</style>
        <div style="margin-top: 1rem;">
            <div style="
                background: #f3f4f6;
                border-radius: 8px;
                height: 12px;
                overflow: hidden;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
            ">
                <div style="
                    background: linear-gradient(90deg, #ed1847 0%, #c41230 100%);
                    height: 100%;
                    width: {progress * 100}%;
                    transition: width 0.5s ease;
                    border-radius: 8px;
                    {stripe_style}
                "></div>
            </div>
            <div style="
                display: flex;
                justify-content: space-between;
                margin-top: 0.5rem;
                font-size: 0.75rem;
                color: #9ca3af;
            ">
                <span>Initiating</span>
                <span>Processing</span>
                <span>Finalizing</span>
            </div>
        </div>
        """
    
    def render_trade_metrics(allocations: List[Dict], placeholder):
        """Render trade execution metrics."""
        if not allocations:
            return
        
        total = len(allocations)
        successful = sum(1 for a in allocations if a.get('status') in ['SUCCESS', 'COMPLETED'])
        failed = sum(1 for a in allocations if a.get('status') == 'FAILED')
        pending = sum(1 for a in allocations if a.get('status') == 'PENDING')
        
        with placeholder.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Trades",
                    value=total,
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Successful",
                    value=successful,
                    delta=f"{(successful/total*100) if total > 0 else 0:.0f}%"
                )
            
            with col3:
                st.metric(
                    label="Failed",
                    value=failed,
                    delta=f"-{failed}" if failed > 0 else None,
                    delta_color="inverse"
                )
            
            with col4:
                st.metric(
                    label="Pending",
                    value=pending,
                    delta=None
                )
    
    def show_final_results(status_data: Dict[str, Any], allocations: List[Dict], placeholder):
        """Display final execution results."""
        status = status_data.get('status', 'UNKNOWN').upper()
        
        with placeholder.container():
            if status in ['COMPLETED', 'SUCCESS']:
                # Success message
                st.success("✓ **Trade Execution Completed Successfully!**")
                
                # Summary stats
                if allocations:
                    successful = sum(1 for a in allocations if a.get('status') in ['SUCCESS', 'COMPLETED'])
                    st.info(f"&#10003; {successful} trade(s) executed successfully")
                
            elif status == 'FAILED':
                # Failure message
                st.error("&#10007; **Trade Execution Failed**")
                
                # Error details
                error_message = status_data.get('message', 'Unknown error occurred')
                st.error(f"Error: {error_message}")
                
                # Show failed trades if available
                if allocations:
                    failed_trades = [a for a in allocations if a.get('status') == 'FAILED']
                    if failed_trades:
                        with st.expander(f"View {len(failed_trades)} Failed Trade(s)"):
                            for trade in failed_trades[:10]:  # Limit to first 10
                                st.write(f"**Trade ID:** {trade.get('id', 'N/A')}")
                                st.write(f"**Error:** {trade.get('error_message', 'Unknown error')}")
                                st.write("---")
                
            elif status == 'TIMEOUT':
                # Timeout message
                st.warning("◷ **Trade Execution Timed Out**")
                st.info("The trades may still be processing. Please check the status later.")
                
            else:
                # Partial or unknown status
                st.warning(f"&#9888; **Trade Execution Status: {status}**")
                
                if allocations:
                    successful = sum(1 for a in allocations if a.get('status') in ['SUCCESS', 'COMPLETED'])
                    failed = sum(1 for a in allocations if a.get('status') == 'FAILED')
                    
                    if successful > 0:
                        st.info(f"&#10003; {successful} trade(s) succeeded")
                    if failed > 0:
                        st.warning(f"&#10007; {failed} trade(s) failed")
    
    # Start monitoring
    start_time = time.time()
    max_duration = api_client.config.get("max_polling_duration", 300)
    poll_interval = api_client.config.get("status_polling_interval", 5)
    
    final_status = None
    allocations = []
    
    # Initial display
    update_status_display({'status': 'PENDING'}, 0)
    
    # Polling loop
    while time.time() - start_time < max_duration:
        elapsed_time = time.time() - start_time
        
        # Get current status
        status_result = api_client.get_group_status(group_id)
        
        # Update display
        update_status_display(status_result, elapsed_time)
        
        # Check current status
        current_status = status_result.get('status', '').upper()
        
        # Get allocations if processing or complete
        if current_status in ['PROCESSING', 'COMPLETED', 'SUCCESS', 'FAILED', 'PARTIAL']:
            allocations_result = api_client.get_all_trade_allocations(group_id)
            if allocations_result.get('success'):
                allocations = allocations_result.get('allocations', [])
                render_trade_metrics(allocations, metrics_placeholder)
        
        # Check for terminal states
        if current_status in ['COMPLETED', 'SUCCESS', 'FAILED', 'REJECTED', 'CANCELLED']:
            final_status = status_result
            final_status['allocations'] = allocations
            final_status['success_count'] = allocations_result.get('success_count', 0) if allocations else 0
            final_status['failed_count'] = allocations_result.get('failed_count', 0) if allocations else 0
            break
        
        # Wait before next poll
        time.sleep(poll_interval)
    
    # Handle timeout
    if not final_status:
        final_status = {
            'status': 'TIMEOUT',
            'message': f'Status polling timed out after {max_duration} seconds',
            'allocations': allocations
        }
    
    # Show final results
    show_final_results(final_status, allocations, details_placeholder)
    
    # Return final status for further processing
    return final_status

def render_status_summary(api_results: Dict[str, Any]):
    """
    Render a summary card of the API execution results.
    
    Args:
        api_results: Formatted API results from trade execution
    """
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #fafbfc 0%, #f4f6f8 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #e9ecef;
    ">
        <h3 style="
            color: #1f2937;
            margin: 0 0 1.5rem 0;
            display: flex;
            align-items: center;
        ">
            <span style="
                background: linear-gradient(135deg, #ed1847 0%, #c41230 100%);
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 0.75rem;
                font-size: 1.25rem;
            ">▦</span>
            Execution Summary
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #6b7280; margin: 0;">Group ID</p>
            <p style="color: #1f2937; font-weight: 600; font-size: 0.875rem;">
                {api_results.get('group_id', 'N/A')[:8]}...
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #6b7280; margin: 0;">Environment</p>
            <p style="color: #1f2937; font-weight: 600;">
                {api_results.get('environment', 'UAT')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #6b7280; margin: 0;">Status</p>
            <p style="color: #1f2937; font-weight: 600;">
                {api_results.get('status', 'PENDING')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Download options
    if st.button("💾 Save Execution Report"):
        report_data = json.dumps(api_results, indent=2)
        st.download_button(
            label="Download JSON Report",
            data=report_data,
            file_name=f"trade_execution_{api_results.get('group_id', 'report')}.json",
            mime="application/json"
        )
