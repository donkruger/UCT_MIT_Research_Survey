"""
Maps trading sheet data to Trade Allocations API payload format.
Handles the transformation from CSV format to API request structure.
"""

import pandas as pd
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import streamlit as st

class TradeDataMapper:
    """Maps CSV/Excel data to Trade Allocations API format."""
    
    # Mapping of trading directions to API action IDs
    ACTION_MAPPING = {
        'BUY': 7,      # Purchase action
        'SELL': 8,     # Redemption action
        'SWITCH': 9    # Switch action (if supported)
    }
    
    # System identifier for this application
    SYSTEM_IDENTIFIER_ID = 27
    
    @staticmethod
    def generate_group_id() -> str:
        """Generate a unique group ID for the batch (UUID format)."""
        return str(uuid.uuid4()).upper()  # Use uppercase UUID to match Postman examples
    
    @classmethod
    def map_csv_to_api(
        cls,
        csv_data: pd.DataFrame,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Map CSV data to Trade Allocations API payload.
        
        Args:
            csv_data: DataFrame containing trade data with columns:
                     ShareCode, ContractCode, InstrumentID, Units, Amount, Direction, UserID, TrustAccount
            metadata: Additional metadata including trader info
            
        Returns:
            API-ready payload for createValueOrdersWithSystemIdentifier endpoint
        """
        metadata = metadata or {}
        # Generate a unique group ID in the correct format
        group_id = cls.generate_group_id()
        batch_timestamp = datetime.now()
        
        # Validate required columns
        required_columns = ['ShareCode', 'ContractCode', 'InstrumentID', 'Units', 'Amount', 'Direction', 'UserID', 'TrustAccount']
        missing_columns = set(required_columns) - set(csv_data.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Build trade allocation requests
        trade_requests = []
        for idx, row in csv_data.iterrows():
            trade_request = cls._build_trade_request(
                row, 
                idx, 
                group_id,
                batch_timestamp,
                len(csv_data),
                metadata
            )
            trade_requests.append(trade_request)
        
        # Build complete payload according to Swagger spec
        payload = {
            "systemIdentifierID": cls.SYSTEM_IDENTIFIER_ID,
            "groupId": group_id,  # Required at root level per Swagger
            "valueTradeAllocationRequestDTOS": trade_requests
        }
        
        # Store mapping audit for tracking
        audit_data = cls._store_mapping_audit(group_id, csv_data, payload, metadata)
        
        return payload
    
    @classmethod
    def _build_trade_request(
        cls,
        row: pd.Series,
        index: int,
        group_id: str,
        batch_timestamp: datetime,
        total_trades: int,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build individual trade request from CSV row.
        
        Args:
            row: DataFrame row containing trade data
            index: Row index
            group_id: Batch group ID
            batch_timestamp: Timestamp for the batch
            total_trades: Total number of trades in batch
            metadata: Additional metadata
            
        Returns:
            Individual trade allocation request
        """
        
        # Generate unique reference for this trade
        unique_ref = f"TSA_{group_id[:8]}_{index:04d}"
        
        # Determine action ID from direction
        direction = str(row['Direction']).upper()
        action_id = cls.ACTION_MAPPING.get(direction, 7)  # Default to BUY if unknown
        
        # Get trader ID from metadata or use default (must not be 0)
        trader_id = metadata.get('trader_id')
        if not trader_id:
            # Try to get from session state or use default
            trader_id = st.session_state.get('trader_id', 45314)
        
        # Handle Amount and Units based on Direction (BUY/SELL business rules)
        # BUY orders: Amount is required (value-based), Units should be 0
        # SELL orders: Units is required (unit-based), Amount should be 0 or null
        import numpy as np
        
        if direction == 'BUY':
            # BUY: Value-based order
            amount = float(row['Amount']) if pd.notna(row['Amount']) else 0.0
            units = 0.0  # Units should be 0 for value-based BUY orders
            cost_calculation_type = 1  # 1 = BUY (value-based)
            price = 50.0  # Default price for value-based orders
        else:  # SELL
            # SELL: Unit-based order
            units = float(row['Units']) if pd.notna(row['Units']) else 0.0
            amount = 0.0  # Amount should be 0 for unit-based SELL orders
            cost_calculation_type = 2  # 2 = SELL (unit-based)
            price = None  # Price can be null for unit-based orders
        
        # Build the trade request according to exact Swagger spec
        trade_request = {
            "userID": int(row['UserID']),
            "instrumentID": int(row['InstrumentID']),
            "price": price,  # Required per Swagger spec for BUY, can be null for SELL
            "trustAccountID": int(row['TrustAccount']),
            "groupId": group_id,  # Required in each request per Swagger
            "depositRequired": False,
            "costCalculationType": cost_calculation_type,  # 1 = BUY, 2 = SELL
            "uniqueTransactionReference": unique_ref,
            "dateCreated": batch_timestamp.strftime("%Y-%m-%d %H:%M"),
            # triggerOnDate behavior:
            # - None/null = immediate execution when markets open
            # - Specific datetime = scheduled execution (must be in UTC)
            # Note: Server is UTC+0, your local may be UTC+2 (South Africa)
            "triggerOnDate": None,  # null for immediate execution
            "trustAccountActionId": action_id,
            "optionalChargeIDs": [0],  # Include as per Swagger spec
            "optionalChargesWithOverrideValues": [
                {
                    "chargeID": 0,
                    "overrideValue": 0
                }
            ],
            "transactionTag": f"{row['ShareCode']}_{direction}_{index}",
            "startAllocationProcessManually": False,
            "isCashMovement": False,
            "allowNegativeMovement": False,
            "traderID": int(trader_id),  # Ensure non-zero
            "totalTradeRequestsInGroup": total_trades,
            "systemIdentifierID": cls.SYSTEM_IDENTIFIER_ID,
            "amount": amount if amount > 0 else None,  # null for SELL orders
            "units": units  # 0 for BUY, actual units for SELL
        }
        
        return trade_request
    
    @staticmethod
    def _store_mapping_audit(
        group_id: str,
        csv_data: pd.DataFrame,
        payload: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store mapping audit trail in session state for tracking and debugging.
        
        Args:
            group_id: Batch group ID
            csv_data: Original CSV data
            payload: Generated API payload
            metadata: Additional metadata
            
        Returns:
            Audit data dictionary
        """
        
        # Calculate summary statistics
        buy_trades = csv_data[csv_data['Direction'].str.upper() == 'BUY']
        sell_trades = csv_data[csv_data['Direction'].str.upper() == 'SELL']
        
        audit_data = {
            'group_id': group_id,
            'timestamp': datetime.now().isoformat(),
            'environment': st.session_state.get('api_environment', 'UAT'),
            'csv_row_count': len(csv_data),
            'csv_summary': {
                'total_trades': len(csv_data),
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'total_buy_amount': float(buy_trades['Amount'].sum()) if len(buy_trades) > 0 else 0.0,
                'total_sell_amount': float(sell_trades['Amount'].sum()) if len(sell_trades) > 0 else 0.0,
                'unique_users': int(csv_data['UserID'].nunique()),
                'unique_instruments': int(csv_data['InstrumentID'].nunique()),
                'unique_accounts': int(csv_data['TrustAccount'].nunique()),
                'share_codes': csv_data['ShareCode'].unique().tolist()
            },
            'metadata': metadata,
            'api_payload_size': len(payload.get('valueTradeAllocationRequestDTOS', [])),
            'system_identifier': TradeDataMapper.SYSTEM_IDENTIFIER_ID
        }
        
        # Store in session state for access by other components
        st.session_state['trade_audit'] = audit_data
        
        return audit_data
    
    @staticmethod
    def format_api_response(response: Dict[str, Any], audit_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format API response for display and email reporting.
        
        Args:
            response: Raw API response
            audit_data: Audit data from mapping
            
        Returns:
            Formatted response data for UI display and email
        """
        
        # Get audit data from session if not provided
        if not audit_data:
            audit_data = st.session_state.get('trade_audit', {})
        
        formatted = {
            'group_id': response.get('groupId', audit_data.get('group_id', 'N/A')),
            'status': response.get('status', 'PENDING'),
            'submitted_at': datetime.now().isoformat(),
            'environment': st.session_state.get('api_environment', 'UAT'),
            'system_identifier': TradeDataMapper.SYSTEM_IDENTIFIER_ID,
            'batch_summary': audit_data.get('csv_summary', {}),
            'trade_count': audit_data.get('csv_row_count', 0),
            'api_response': {
                'success': response.get('success', False),
                'message': response.get('message', ''),
                'status_code': response.get('status_code', 0)
            }
        }
        
        # Add allocation details if available
        if 'allocations' in response:
            allocations = response['allocations']
            formatted['execution_summary'] = {
                'total_allocations': len(allocations),
                'successful': sum(1 for a in allocations if a.get('status') == 'SUCCESS'),
                'failed': sum(1 for a in allocations if a.get('status') == 'FAILED'),
                'pending': sum(1 for a in allocations if a.get('status') == 'PENDING')
            }
            
            # Add failed trade details if any
            failed_trades = [a for a in allocations if a.get('status') == 'FAILED']
            if failed_trades:
                formatted['failed_trades'] = [
                    {
                        'id': trade.get('id'),
                        'error': trade.get('error_message', 'Unknown error'),
                        'reference': trade.get('uniqueTransactionReference')
                    }
                    for trade in failed_trades[:5]  # Limit to first 5 for brevity
                ]
        
        return formatted
    
    @staticmethod
    def validate_csv_data(csv_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate CSV data before API submission.
        
        Args:
            csv_data: DataFrame to validate
            
        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        # Check required columns
        required_columns = ['ShareCode', 'ContractCode', 'InstrumentID', 'Units', 'Amount', 'Direction', 'UserID', 'TrustAccount']
        missing_columns = set(required_columns) - set(csv_data.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate Direction values
        valid_directions = ['BUY', 'SELL']
        invalid_directions = ~csv_data['Direction'].str.upper().isin(valid_directions)
        if invalid_directions.any():
            invalid_values = csv_data.loc[invalid_directions, 'Direction'].unique().tolist()
            errors.append(f"Invalid Direction values: {invalid_values}. Must be BUY or SELL")
        
        # Check for negative amounts
        if (csv_data['Amount'] <= 0).any():
            errors.append("Amount must be positive values")
        
        # Check for valid user IDs
        if csv_data['UserID'].isnull().any():
            errors.append("UserID cannot be null")
        
        # Check for valid instrument IDs
        if csv_data['InstrumentID'].isnull().any():
            errors.append("InstrumentID cannot be null")
        
        # Check for valid trust accounts
        if csv_data['TrustAccount'].isnull().any():
            errors.append("TrustAccount cannot be null")
        
        # Warnings
        # Check for duplicate trades
        duplicates = csv_data.duplicated(subset=['UserID', 'InstrumentID', 'Amount', 'Direction'], keep=False)
        if duplicates.any():
            warnings.append(f"Found {duplicates.sum()} potential duplicate trades")
        
        # Check contract code format
        for idx, row in csv_data.iterrows():
            expected_contract = f"UT.ZA.{row['ShareCode']}"
            if row['ContractCode'] != expected_contract:
                warnings.append(f"Row {idx+1}: Contract code mismatch. Expected {expected_contract}, got {row['ContractCode']}")
                break  # Only show first warning
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
