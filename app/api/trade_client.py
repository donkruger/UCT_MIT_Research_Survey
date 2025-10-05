"""
Trade Allocations API client for executing trades.
Implements integration with EasyEquities Trade Allocations Monitor API.
"""

import requests
import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import json

class TradeAllocationsClient:
    """Client for interacting with Trade Allocations API."""
    
    def __init__(self):
        """Initialize client with configuration from secrets."""
        # Get configuration from secrets, with fallback defaults
        try:
            self.config = st.secrets.get("trade_api", {})
        except:
            # Default configuration if secrets not set
            self.config = {
                "environment": "uat",
                "uat_base_url": "https://tradeallocationsapi.purple-uat.easyequities.io",
                "uat_monitor_url": "https://trade-allocations-monitor.purple-uat.easyequities.io",
                "system_identifier_id": 27,
                "api_timeout": 30,
                "max_retry_attempts": 3,
                "status_polling_interval": 5,
                "max_polling_duration": 300
            }
        
        self.environment = self.config.get("environment", "uat")
        self.base_url = self.config.get(f"{self.environment}_base_url", self.config.get("uat_base_url"))
        self.monitor_url = self.config.get(f"{self.environment}_monitor_url", self.config.get("uat_monitor_url"))
        self.system_id = self.config.get("system_identifier_id", 27)
        self.timeout = self.config.get("api_timeout", 30)
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Add authentication if provided
        if "api_key" in self.config:
            self.session.headers["Authorization"] = f"Bearer {self.config['api_key']}"
    
    def create_value_orders(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit value orders to the Trade Allocations API.
        
        Args:
            payload: API payload containing trade requests
            
        Returns:
            API response with groupId and status
        """
        endpoint = f"{self.base_url}/tradeallocations/monitored/order/createValueOrdersWithSystemIdentifier"
        
        try:
            # Store request for troubleshooting
            st.session_state['last_api_request'] = {
                'endpoint': endpoint,
                'timestamp': datetime.now().isoformat(),
                'trade_count': len(payload.get('valueTradeAllocationRequestDTOS', [])),
                'environment': self.environment.upper(),
                'full_payload': payload  # Store the complete payload
            }
            
            # Show the exact endpoint being called
            st.info(f"&#8599; Submitting trades to: `{endpoint}`")
            
            # Log the request for debugging
            with st.expander("📦 First Leg: API Payload Details", expanded=False):
                st.markdown("**Endpoint:**")
                st.code(endpoint)
                st.markdown("**Complete Payload:**")
                # Show the full payload being sent
                st.json(payload)
                st.markdown("**Summary:**")
                st.info(f"""
                - Environment: {self.environment.upper()}
                - System ID: {payload.get('systemIdentifierID')}
                - Group ID: {payload.get('groupId')}
                - Trades: {len(payload.get('valueTradeAllocationRequestDTOS', []))}
                """)
            
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            # Store response for troubleshooting
            st.session_state['last_api_response'] = {
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat(),
                'response_text': response.text[:500] if response.text else None
            }
            
            # Check if request was successful
            if response.status_code == 200:
                # Parse the simple response format: {"groupID": "string"}
                result = response.json() if response.text else {}
                
                # Extract group ID from response (note: API returns "groupID" not "groupId")
                group_id = result.get('groupID') or result.get('groupId') or payload.get('groupId')
                
                # Log the returned group ID for clarity
                st.success(f"&#10003; **Orders submitted successfully!**")
                st.code(f"Returned Group ID: {group_id}")
                
                return {
                    'success': True,
                    'groupId': group_id,
                    'response': result,
                    'message': f'&#10003; Orders submitted successfully (Group: {group_id[:8]}...)',
                    'status_code': response.status_code,
                    'endpoint': endpoint
                }
            else:
                # Handle non-200 responses with better error messages
                error_detail = self._parse_error_response(response)
                
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}",
                    'message': error_detail,
                    'status_code': response.status_code,
                    'response': response.text,
                    'endpoint': endpoint,
                    'troubleshooting': self._get_troubleshooting_tips(response.status_code)
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'message': f'The API request timed out after {self.timeout} seconds. Please try again.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Connection failed',
                'message': 'Could not connect to the API server. Please check your network connection.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'API request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Unexpected error: {str(e)}'
            }
    
    def get_group_status(self, group_id: str) -> Dict[str, Any]:
        """
        Query the status of a trade group.
        
        Args:
            group_id: The group identifier from order creation
            
        Returns:
            Status information for the trade group
        """
        endpoint = f"{self.monitor_url}/tradeGroupStatus/{group_id}"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            
            # Gracefully handle 404 as "PENDING"
            if response.status_code == 404:
                return {
                    'success': True,
                    'status': 'PENDING',
                    'data': {'overallStatus': 0}, # Incomplete
                    'message': 'Trade group not yet registered. Status is PENDING.'
                }
            
            if response.status_code == 200:
                data = response.json() if response.text else {}
                
                # Parse the status from response
                status = data.get('status', 'UNKNOWN')
                
                return {
                    'success': True,
                    'status': status,
                    'data': data,
                    'message': data.get('message', f'Status: {status}')
                }
            else:
                return {
                    'success': False,
                    'error': f"Status code: {response.status_code}",
                    'status': 'ERROR',
                    'message': f'Failed to get status: HTTP {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'ERROR',
                'message': f'Failed to get status: {str(e)}'
            }
    
    def get_all_trade_allocations(self, group_id: str) -> Dict[str, Any]:
        """
        Get detailed information for all trades in a group.
        
        Args:
            group_id: The group identifier
            
        Returns:
            Detailed trade allocation information including failure reasons
        """
        endpoint = f"{self.monitor_url}/trade-monitor/allocation/all/{group_id}"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json() if response.text else []
                
                # Process allocations
                allocations = data if isinstance(data, list) else []
                
                # Parse allocation statuses
                # allocationStatusId: 3 = FAILED, 4 = SUCCESS, 0 = PENDING
                success_count = 0
                failed_count = 0
                pending_count = 0
                failed_trades = []
                successful_trades = []
                
                for allocation in allocations:
                    status_id = allocation.get('allocationStatusId')
                    
                    if status_id == 4:  # SUCCESS
                        success_count += 1
                        successful_trades.append({
                            'userID': allocation.get('userID'),
                            'instrumentID': allocation.get('instrumentID'),
                            'amount': allocation.get('amount'),
                            'units': allocation.get('units'),
                            'transactionTag': allocation.get('transactionTag'),
                            'transactionID': allocation.get('transactionID')
                        })
                    elif status_id == 3:  # FAILED
                        failed_count += 1
                        failure_reason = allocation.get('failureReason', 'Unknown error')
                        
                        # Parse nested error messages if present
                        if 'message' in str(failure_reason):
                            try:
                                import json
                                if 'Failed to process OrderAllocation:' in failure_reason:
                                    # Extract the JSON part
                                    json_str = failure_reason.split('Failed to process OrderAllocation: ')[-1]
                                    error_data = json.loads(json_str)
                                    failure_reason = error_data.get('message', failure_reason)
                            except:
                                pass  # Use original message if parsing fails
                        
                        failed_trades.append({
                            'userID': allocation.get('userID'),
                            'instrumentID': allocation.get('instrumentID'),
                            'amount': allocation.get('amount'),
                            'units': allocation.get('units'),
                            'transactionTag': allocation.get('transactionTag'),
                            'uniqueTransactionReference': allocation.get('uniqueTransactionReference'),
                            'failureReason': failure_reason,
                            'trustAccountID': allocation.get('trustAccountID')
                        })
                    else:  # PENDING or other
                        pending_count += 1
                
                return {
                    'success': True,
                    'allocations': allocations,
                    'count': len(allocations),
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'pending_count': pending_count,
                    'successful_trades': successful_trades,
                    'failed_trades': failed_trades,
                    'message': f'Retrieved {len(allocations)} trade allocations'
                }
            else:
                return {
                    'success': False,
                    'error': f"Status code: {response.status_code}",
                    'allocations': [],
                    'failed_trades': [],
                    'successful_trades': [],
                    'message': f'Failed to get allocations: HTTP {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'allocations': [],
                'failed_trades': [],
                'successful_trades': [],
                'message': f'Failed to get allocations: {str(e)}'
            }
    
    def poll_status(self, group_id: str, callback=None) -> Dict[str, Any]:
        """
        Poll for trade group status until completion or timeout.
        
        Args:
            group_id: The group identifier
            callback: Optional callback function for status updates
            
        Returns:
            Final status information
        """
        max_duration = self.config.get("max_polling_duration", 300)
        interval = self.config.get("status_polling_interval", 5)
        start_time = time.time()
        
        last_status = None
        
        # Show exactly what URL we're polling
        poll_url = f"{self.monitor_url}/tradeGroupStatus/{group_id}"
        st.info(f"⌕ Polling for status of Group ID: `{group_id}`")
        
        # Show payload details that affect execution
        with st.expander("📡 Polling Details & Payload Info", expanded=False):
            st.code(f"Polling URL: {poll_url}")
            st.code(f"Max Duration: {max_duration}s | Interval: {interval}s")
            st.markdown("**Key Payload Settings:**")
            st.code('"startAllocationProcessManually": false  // Sets allocationStatusId to 0 (auto-execute)')
            st.code('"triggerOnDate": null  // Immediate execution when markets open')
            st.markdown("**Important Timezone Notes:**")
            st.info("◷ Server Time: UTC+0 | Your Time: Likely UTC+2 (SA)")
            st.info("◈ For scheduled execution, adjust for 2-hour difference")
            st.markdown("**Status Values:**")
            st.code("groupStatusID: 0 = incomplete, 1 = success, 2 = complete with errors")
            st.markdown("**Important:** Status 2 = API success with business errors (expected for insufficient funds)")
        
        while time.time() - start_time < max_duration:
            # Get current status
            status_result = self.get_group_status(group_id)
            
            # Call callback if provided
            if callback:
                callback(status_result)
            
            # Check for terminal states - API returns 'groupStatusID' (not 'overallStatus')
            # Based on Johan's response: groupStatusID values:
            # 0 = incomplete, 1 = group successful, 2 = group complete with errors
            if status_result.get('success') and 'data' in status_result and status_result['data']:
                data = status_result['data']
                
                # The API returns 'groupStatusID' as the main status field
                group_status_id = data.get('groupStatusID') or data.get('overallStatus')
                
                # Extract business metrics from response
                total_success = data.get('totalSuccess', 0)
                total_failed = data.get('totalFailed', 0)
                total_trades = data.get('totalTradesInGroup', 0)
                group_status_text = data.get('groupStatus', '')
                
                # Display current status for debugging
                st.info(f"▦ Status: {group_status_text} (ID: {group_status_id}) | Success: {total_success} | Failed: {total_failed} | Total: {total_trades}")
                
                if group_status_id in [1, 2]: # Terminal states
                    # Both status 1 and 2 are completion states
                    # Status 2 means "Complete with Failures" but is still a successful API operation
                    
                    # Get final allocation details for the complete report
                    allocations_result = self.get_all_trade_allocations(group_id)
                    status_result['allocations'] = allocations_result.get('allocations', [])
                    status_result['success_count'] = total_success
                    status_result['failed_count'] = total_failed
                    status_result['total_trades'] = total_trades
                    
                    # Map groupStatusID to descriptive status
                    if group_status_id == 1:
                        status_result['final_status'] = 'COMPLETED_SUCCESS'
                        status_result['success'] = True
                    elif group_status_id == 2:
                        status_result['final_status'] = 'COMPLETED_WITH_BUSINESS_ERRORS'
                        status_result['success'] = True  # Still successful API operation
                    
                    # Add business error context
                    status_result['execution_summary'] = {
                        'group_status': group_status_text,
                        'total_trades': total_trades,
                        'successful_trades': total_success,
                        'failed_trades': total_failed,
                        'completion_type': 'Business rule violations' if group_status_id == 2 else 'All trades successful'
                    }
                    
                    return status_result
            
            last_status = status_result
            time.sleep(interval)
        
        # Timeout reached
        st.warning("Polling timed out. Returning last known status.")
        
        timeout_result = {
            'success': False,
            'status': 'TIMEOUT',
            'message': f'Status polling timed out after {max_duration} seconds.',
            'last_status': last_status
        }
        
        # Try to get final allocations one last time on timeout
        allocations_result = self.get_all_trade_allocations(group_id)
        if allocations_result['success']:
            timeout_result['allocations'] = allocations_result.get('allocations', [])
            timeout_result['success_count'] = allocations_result.get('success_count', 0)
            timeout_result['failed_count'] = allocations_result.get('failed_count', 0)

        return timeout_result
    
    def test_connection(self) -> bool:
        """
        Test connection to the API endpoints.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to access the base URL
            response = self.session.get(
                f"{self.base_url}/health",  # Assuming there's a health endpoint
                timeout=5
            )
            return response.status_code in [200, 404]  # 404 is OK, means server responded
        except:
            try:
                # Try monitor URL as fallback
                response = self.session.get(
                    f"{self.monitor_url}/health",
                    timeout=5
                )
                return response.status_code in [200, 404]
            except:
                return False
    
    def _parse_error_response(self, response) -> str:
        """Parse error response for user-friendly message."""
        try:
            if response.text:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'message': response.text}
                return error_data.get('message', response.text[:200])
        except:
            pass
        
        # Default error messages based on status code
        error_messages = {
            400: "Invalid request format. Please check the trade data.",
            401: "Authentication failed. Please check API credentials.",
            403: "Access denied. System identifier may not have permission.",
            404: "API endpoint not found. Please check configuration.",
            422: "Validation error. One or more trades have invalid data.",
            429: "Rate limit exceeded. Please wait before retrying.",
            500: "Server error. Please try again later.",
            502: "Gateway error. API service may be temporarily unavailable.",
            503: "Service unavailable. Please try again later."
        }
        
        return error_messages.get(response.status_code, f"Unknown error (Status {response.status_code})")
    
    def _get_troubleshooting_tips(self, status_code: int) -> List[str]:
        """Get troubleshooting tips based on status code."""
        tips = {
            400: [
                "Check that all required fields are present in the CSV",
                "Verify Direction values are 'BUY' or 'SELL'",
                "Ensure Amount values are positive numbers",
                "Confirm InstrumentID and UserID are valid"
            ],
            401: [
                "Verify API credentials in .streamlit/secrets.toml",
                "Check if API key has expired",
                "Ensure Bearer token format is correct"
            ],
            403: [
                "Confirm system identifier ID is 27",
                "Check if your system has permission for this operation",
                "Verify the environment (UAT/QA/PROD) access"
            ],
            422: [
                "Review the specific validation errors in the response",
                "Check if UserID exists in the system",
                "Verify InstrumentID is valid for trading",
                "Ensure TrustAccount is properly configured"
            ],
            500: [
                "Wait a few minutes and try again",
                "Check the API status page",
                "Contact support if the issue persists"
            ]
        }
        
        return tips.get(status_code, ["Check the API response for details", "Contact technical support if issue persists"])
