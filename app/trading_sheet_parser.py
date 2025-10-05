"""
Trading Sheet Parser Module
Handles parsing and validation of trading sheet uploads (CSV/Excel)
Prepares data for AccountProcessor API integration
"""

import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib
from io import BytesIO

class TradingSheetParser:
    """Parser for trading sheet uploads with validation and API preparation"""
    
    REQUIRED_COLUMNS = [
        'ShareCode', 'ContractCode', 'InstrumentID', 
        'Amount', 'Direction', 'UserID', 'TrustAccount'
    ]
    
    # Units is now optional for value-based trades
    OPTIONAL_COLUMNS = ['Units']
    
    VALID_DIRECTIONS = ['BUY', 'SELL']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.parsed_data = None
        self.raw_data = None
        
    def parse_file(self, file_content: bytes, filename: str) -> Tuple[bool, Optional[pd.DataFrame]]:
        """
        Parse uploaded file (CSV or Excel) and validate structure
        
        Args:
            file_content: File content as bytes
            filename: Name of the uploaded file
            
        Returns:
            Tuple of (success: bool, data: pd.DataFrame or None)
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Determine file type and parse accordingly
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(BytesIO(file_content))
            elif filename.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(BytesIO(file_content))
            else:
                self.errors.append(f"Unsupported file format: {filename}")
                return False, None
            
            self.raw_data = df
            
            # Add 'Units' column if it's missing, defaulting to 0 for value orders
            if 'Units' not in df.columns:
                df['Units'] = 0
                self.warnings.append("'Units' column not found; proceeding with value-based trades (units=0).")
            
            # Validate columns
            if not self._validate_columns(df):
                return False, None
            
            # Clean and validate data
            df = self._clean_data(df)
            
            # Validate business rules
            if not self._validate_business_rules(df):
                return False, None
            
            self.parsed_data = df
            return True, df
            
        except Exception as e:
            self.errors.append(f"Error parsing file: {str(e)}")
            return False, None
    
    def _validate_columns(self, df: pd.DataFrame) -> bool:
        """Validate that all required columns are present"""
        # Check for all columns (required + optional present)
        all_expected_columns = self.REQUIRED_COLUMNS + self.OPTIONAL_COLUMNS
        
        # Check for required columns, now that 'Units' is optional at upload
        # We ensure 'Units' exists before this check.
        current_required = [col for col in all_expected_columns if col in df.columns]

        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            self.errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        return True
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data"""
        df = df.copy()
        
        # Strip whitespace from string columns
        string_columns = ['ShareCode', 'ContractCode', 'Direction']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Ensure numeric types
        numeric_columns = {
            'InstrumentID': 'int64',
            'Units': 'float64',
            'Amount': 'float64',
            'UserID': 'int64',
            'TrustAccount': 'int64'
        }
        
        for col, dtype in numeric_columns.items():
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    self.warnings.append(f"Some values in {col} could not be converted to numbers")
        
        return df
    
    def _validate_business_rules(self, df: pd.DataFrame) -> bool:
        """Validate business rules for the trading data"""
        valid = True
        
        # Check for null values - BUT EXCLUDE Amount/Units based on Direction
        # BUY orders need Amount, SELL orders need Units
        # This is now handled in comprehensive validation, so only check other required fields
        essential_cols = ['ShareCode', 'ContractCode', 'InstrumentID', 'Direction', 'UserID', 'TrustAccount']
        check_cols = [col for col in essential_cols if col in df.columns]
        null_check = df[check_cols].isnull().sum()
        if null_check.any():
            null_columns = null_check[null_check > 0].index.tolist()
            self.errors.append(f"Null values found in required columns: {', '.join(null_columns)}")
            valid = False
        
        # Validate Direction values
        invalid_directions = ~df['Direction'].isin(self.VALID_DIRECTIONS)
        if invalid_directions.any():
            invalid_values = df.loc[invalid_directions, 'Direction'].unique().tolist()
            self.errors.append(f"Invalid Direction values: {invalid_values}. Must be BUY or SELL")
            valid = False
        
        # ===========================================
        # COMPREHENSIVE VALIDATION: BUY/SELL + UT-Only
        # ===========================================
        if not self._validate_comprehensive_business_rules(df):
            valid = False
        
        # Check for duplicate trades (warning only)
        # Exclude units from duplicate check for value orders
        dup_check_cols = [col for col in self.REQUIRED_COLUMNS if col != 'Units']
        duplicates = df.duplicated(subset=dup_check_cols, keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            self.warnings.append(f"Found {dup_count} potential duplicate rows in the trading sheet")
        
        return valid
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics of the parsed data"""
        if self.parsed_data is None:
            return {}
        
        df = self.parsed_data
        
        return {
            'total_trades': len(df),
            'buy_trades': len(df[df['Direction'] == 'BUY']),
            'sell_trades': len(df[df['Direction'] == 'SELL']),
            'unique_shares': df['ShareCode'].nunique(),
            'unique_users': df['UserID'].nunique(),
            'unique_accounts': df['TrustAccount'].nunique(),
            'total_buy_amount': df[df['Direction'] == 'BUY']['Amount'].sum(),
            'total_sell_amount': df[df['Direction'] == 'SELL']['Amount'].sum(),
            'total_sell_units': df[df['Direction'] == 'SELL']['Units'].sum(),
            'trades_by_share': df.groupby('ShareCode').size().to_dict(),
            'trades_by_direction': df.groupby('Direction').size().to_dict()
        }
    
    def prepare_api_payload(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for AccountProcessor API submission
        
        Args:
            metadata: Additional metadata (user info, timestamp, etc.)
            
        Returns:
            API-ready payload structure
        """
        if self.parsed_data is None:
            return {}
        
        # Convert DataFrame to list of dictionaries
        trades = self.parsed_data.to_dict('records')
        
        # Generate batch ID
        batch_id = self._generate_batch_id(metadata.get('user_email', ''), 
                                          metadata.get('timestamp', datetime.now()))
        
        payload = {
            'batch_id': batch_id,
            'submission_timestamp': metadata.get('timestamp', datetime.now().isoformat()),
            'trader_info': {
                'full_name': metadata.get('user_name', ''),
                'email': metadata.get('user_email', ''),
                'user_id': metadata.get('system_user_id', '')
            },
            'declaration': {
                'accepted': metadata.get('declaration_accepted', False),
                'timestamp': metadata.get('declaration_timestamp', ''),
                'ip_address': metadata.get('ip_address', '')
            },
            'file_info': {
                'original_filename': metadata.get('filename', ''),
                'file_size': metadata.get('file_size', 0),
                'file_hash': self._calculate_file_hash(self.raw_data),
                'upload_timestamp': metadata.get('upload_timestamp', '')
            },
            'summary': self.get_summary_statistics(),
            'trades': trades,
            'validation': {
                'errors': self.errors,
                'warnings': self.warnings,
                'validated_at': datetime.now().isoformat()
            },
            'processing_status': 'PENDING',
            'api_version': '1.0'
        }
        
        return payload
    
    def _generate_batch_id(self, user_email: str, timestamp: datetime) -> str:
        """Generate a unique batch ID for the submission"""
        data = f"{user_email}{timestamp.isoformat()}"
        hash_obj = hashlib.sha256(data.encode())
        return f"BATCH_{timestamp.strftime('%Y%m%d')}_{hash_obj.hexdigest()[:8].upper()}"
    
    def _calculate_file_hash(self, df: pd.DataFrame) -> str:
        """Calculate hash of the file data for integrity checking"""
        if df is None:
            return ""
        data_str = df.to_csv(index=False)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def format_for_display(self) -> List[Dict[str, Any]]:
        """Format parsed data for display in the UI"""
        if self.parsed_data is None:
            return []
        
        display_data = []
        for idx, row in self.parsed_data.iterrows():
            display_data.append({
                'row_number': idx + 1,
                'ShareCode': row['ShareCode'],
                'ContractCode': row['ContractCode'],
                'InstrumentID': int(row['InstrumentID']),
                'Units': f"{row['Units']:.8f}",
                'Amount': f"R {row['Amount']:,.2f}",
                'Direction': row['Direction'],
                'UserID': int(row['UserID']),
                'TrustAccount': int(row['TrustAccount']),
                'direction_color': '#10b981' if row['Direction'] == 'BUY' else '#ef4444'
            })
        
        return display_data
    
    def _validate_comprehensive_business_rules(self, df: pd.DataFrame) -> bool:
        """
        SECURITY-CRITICAL: Comprehensive validation for UT-only protection and BUY/SELL business rules
        
        This method validates:
        1. BUY/SELL + Amount/Units business rules
        2. Non-UT trades (security protection)
        3. Malicious input patterns (security hardening)
        
        BUSINESS RULES:
        - BUY orders: Must have positive Amount, Units can be empty/0
        - SELL orders: Must have positive Units, Amount can be empty/0
        
        Returns:
            bool: True if all validation passes, False if any blocked
        """
        from app.utils import get_trade_protection_config
        import streamlit as st
        import numpy as np
        import re
        
        # Get validated configuration (with fail-safe defaults)
        protection_config = get_trade_protection_config()
        
        # SECURITY: Always validate in strict mode for production
        environment = st.secrets.get('trade_api', {}).get('environment', 'uat')
        if environment == 'prod':
            protection_config['block_non_ut_trades'] = True
            protection_config['protection_mode'] = 'strict'
        
        # AUDIT: Log validation attempt
        validation_attempt = {
            'timestamp': datetime.now().isoformat(),
            'total_contracts': len(df),
            'environment': environment,
            'protection_enabled': protection_config['block_non_ut_trades']
        }
        
        validation_errors = []
        validation_passed = True
        
        # ===========================================
        # BUSINESS RULE VALIDATION: BUY/SELL Logic
        # ===========================================
        
        buy_sell_errors = []
        
        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel row numbering
            direction = row['Direction']
            amount = row['Amount']
            units = row['Units']
            
            # Convert to numeric, handling NaN/empty values
            amount_val = pd.to_numeric(amount, errors='coerce') if pd.notna(amount) else None
            units_val = pd.to_numeric(units, errors='coerce') if pd.notna(units) else None
            
            if direction == 'BUY':
                # BUY RULE: Must have positive Amount, Units can be empty/0
                if amount_val is None or amount_val <= 0:
                    buy_sell_errors.append(
                        f"Row {row_num}: BUY orders must specify a positive Amount value. "
                        f"Found Amount: {amount if pd.notna(amount) else 'empty'}"
                    )
                
                # BUY orders should have empty or 0 Units (optional validation)
                if units_val is not None and units_val > 0:
                    self.warnings.append(
                        f"Row {row_num}: BUY order has both Amount ({amount_val}) and Units ({units_val}). "
                        f"Amount will be used for value-based order."
                    )
                    
            elif direction == 'SELL':
                # SELL RULE: Must have positive Units, Amount can be empty/0
                if units_val is None or units_val <= 0:
                    buy_sell_errors.append(
                        f"Row {row_num}: SELL orders must specify a positive Units value. "
                        f"Found Units: {units if pd.notna(units) else 'empty'}"
                    )
                
                # SELL orders should have empty or 0 Amount (optional validation)
                if amount_val is not None and amount_val > 0:
                    self.warnings.append(
                        f"Row {row_num}: SELL order has both Units ({units_val}) and Amount ({amount_val}). "
                        f"Units will be used for unit-based order."
                    )
        
        if buy_sell_errors:
            self.errors.extend(buy_sell_errors)
            validation_passed = False
        
        # ===========================================
        # SECURITY VALIDATION: UT-Only Protection
        # ===========================================
        
        if protection_config['block_non_ut_trades']:
            # SECURITY: Input sanitization and validation
            invalid_contracts = []
            suspicious_patterns = []
            
            supported_prefixes = protection_config['supported_prefixes']
            
            for idx, row in df.iterrows():
                contract_code = str(row['ContractCode']).strip()
                
                # SECURITY: Detect suspicious patterns
                if len(contract_code) > 50:  # Abnormally long contract codes
                    suspicious_patterns.append(f"Row {idx+2}: Unusually long ContractCode ({len(contract_code)} chars)")
                
                if re.search(r'[<>"\';\\]', contract_code):  # Potential injection attempts
                    suspicious_patterns.append(f"Row {idx+2}: Suspicious characters in ContractCode")
                
                # CORE VALIDATION: Check against supported prefixes
                is_valid = any(contract_code.startswith(prefix) for prefix in supported_prefixes)
                
                if not is_valid:
                    # Extract potential trade type for reporting
                    detected_type = 'Unknown'
                    if contract_code.startswith('EQ.ZA'):
                        detected_type = 'Equity'
                    elif contract_code.startswith('BD.ZA'):
                        detected_type = 'Bond'
                    elif contract_code.startswith('ETF.ZA'):
                        detected_type = 'ETF'
                    
                    invalid_contracts.append({
                        'row': idx + 2,  # Excel row numbering
                        'contract_code': contract_code,
                        'detected_type': detected_type,
                        'share_code': row.get('ShareCode', 'Unknown')
                    })
            
            # SECURITY: Log suspicious patterns
            if suspicious_patterns:
                validation_attempt['suspicious_patterns'] = suspicious_patterns
                validation_attempt['risk_level'] = 'CRITICAL'
            
            if invalid_contracts:
                self.errors.append(self._generate_ut_protection_error_message(invalid_contracts, protection_config))
                validation_passed = False
        
        else:
            # AUDIT: Log when protection is disabled
            validation_attempt['action'] = 'PROTECTION_DISABLED'
            validation_attempt['risk_level'] = 'HIGH'
        
        # ALSO CHECK OLD CONTRACT CODE FORMAT (warning only)
        invalid_contracts_format = []
        for idx, row in df.iterrows():
            expected_contract = f"UT.ZA.{row['ShareCode']}"
            if row['ContractCode'] != expected_contract:
                invalid_contracts_format.append(f"Row {idx+2}: Expected {expected_contract}, got {row['ContractCode']}")
        
        if invalid_contracts_format:
            self.warnings.append(f"ContractCode format issues: {'; '.join(invalid_contracts_format[:3])}")
            if len(invalid_contracts_format) > 3:
                self.warnings.append(f"... and {len(invalid_contracts_format)-3} more")
        
        # ===========================================
        # FINALIZE VALIDATION RESULTS
        # ===========================================
        
        # AUDIT: Complete validation attempt logging
        validation_attempt.update({
            'business_rule_errors': len(buy_sell_errors),
            'invalid_contracts_count': len(invalid_contracts) if protection_config['block_non_ut_trades'] else 0,
            'suspicious_patterns_count': len(suspicious_patterns) if protection_config['block_non_ut_trades'] else 0,
            'action': 'BLOCKED' if not validation_passed else 'ALLOWED'
        })
        
        self._audit_validation_attempt(validation_attempt)
        
        return validation_passed
    
    def _audit_validation_attempt(self, attempt: Dict[str, Any]):
        """
        Comprehensive audit logging for all validation attempts
        """
        import streamlit as st
        
        try:
            if 'validation_audit_log' not in st.session_state:
                st.session_state['validation_audit_log'] = []
            st.session_state['validation_audit_log'].append(attempt)
            
            # SECURITY: Alert on suspicious activity
            if attempt.get('risk_level') == 'CRITICAL':
                st.session_state['security_alerts'] = st.session_state.get('security_alerts', []) + [attempt]
                
        except Exception:
            pass  # Don't fail validation if audit logging fails
    
    def _generate_ut_protection_error_message(self, invalid_contracts: List[Dict], config: Dict) -> str:
        """
        Generate comprehensive, security-focused error message
        """
        contract_count = len(invalid_contracts)
        contract_list = [f"Row {c['row']}: {c['contract_code']} (detected: {c['detected_type']})" 
                        for c in invalid_contracts[:5]]  # Limit display
        
        if contract_count > 5:
            contract_list.append(f"... and {contract_count - 5} more invalid contracts")
        
        return f"""SECURITY BLOCK: Non-Unit Trust trades detected and blocked.
    
This application is configured for Unit Trust (UT) trades only.
    
&#10007; {contract_count} invalid ContractCode(s) found:
{chr(10).join(f'   • {item}' for item in contract_list)}
    
&#10003; Required format: All ContractCodes must start with '{"', '".join(config['supported_prefixes'])}'
    
To proceed:
1. Remove all non-UT trades from your file
2. Ensure all ContractCodes follow the UT.ZA.{{ShareCode}} format
3. Re-upload the corrected file
    
For assistance, contact the trading desk with this error reference."""
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get detailed validation report"""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'row_count': len(self.parsed_data) if self.parsed_data is not None else 0,
            'column_count': len(self.REQUIRED_COLUMNS)
        }

# Utility functions for streamlit integration
def process_uploaded_file(file_content: bytes, filename: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Process an uploaded trading sheet file
    
    Returns:
        Tuple of (success, result_data)
    """
    parser = TradingSheetParser()
    success, data = parser.parse_file(file_content, filename)
    
    if success:
        return True, {
            'parser': parser,
            'data': data,
            'summary': parser.get_summary_statistics(),
            'display_data': parser.format_for_display(),
            'validation': parser.get_validation_report()
        }
    else:
        return False, {
            'errors': parser.errors,
            'warnings': parser.warnings
        }
