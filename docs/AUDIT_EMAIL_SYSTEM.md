# Comprehensive Audit Email System

## Overview

The Trading Sheet Application implements a **comprehensive audit trail system** that sends detailed emails for **ALL submission attempts** - successful, failed, or error conditions. This ensures complete auditability and compliance with regulatory requirements.

## Key Features

### 1. Universal Coverage
- ✅ **Successful Submissions**: Complete execution details with Group IDs
- ⚠️ **Failed Submissions**: Validation errors, API failures, business rule violations
- ❌ **Error Conditions**: Unexpected errors with full debugging information

### 2. WHO Executed (Authentication-Agnostic)

The system captures user identity through an **authentication-agnostic** architecture:

**Current Implementation:**
- Name and email from Declaration page
- Declaration timestamp
- Authentication method: "declaration"

**Future-Ready For:**
```python
# OAuth/SSO Integration
if 'user' in st.session_state and hasattr(st.session_state.user, 'email'):
    identity['name'] = st.session_state.user.name
    identity['email'] = st.session_state.user.email
    identity['auth_method'] = 'oauth'
    identity['user_id'] = st.session_state.user.id

# API Key Authentication
elif 'api_key_user' in st.session_state:
    identity['name'] = st.session_state.api_key_user['name']
    identity['email'] = st.session_state.api_key_user['email']
    identity['auth_method'] = 'api_key'
    identity['user_id'] = st.session_state.api_key_user['id']
```

### 3. WHAT Was Executed

Complete trading details included:
- **File Information**: Original filename, upload timestamp
- **Trade Metrics**: 
  - Total trades
  - Buy orders (count + amount)
  - Sell orders (count + units)
  - Unique accounts
- **Trade Data**: Full DataFrame with all rows

### 4. WHEN 

Precise timestamps for:
- Submission time
- Declaration date
- Each validation/execution step
- Error occurrence

### 5. OUTCOME

Comprehensive results:
- **Success**: Group ID, API status, environment, system ID
- **With Failures**: Individual trade failure reasons
- **Validation Errors**: Specific rule violations
- **API Errors**: Detailed error messages and responses
- **System Errors**: Exception types, messages, debugging info

### 6. Evidence Attachments

Every audit email includes:
1. **Original CSV File**: Exact file uploaded by user
2. **API Results (JSON)**: Complete execution response
3. **Error Details (JSON)**: Full error information (if applicable)

## Email Format

### Subject Line
```
✅ Trading Sheet Audit Trail - SUCCESS - 20251003_123045
⚠️ Trading Sheet Audit Trail - FAILED - 20251003_123045
❌ Trading Sheet Audit Trail - ERROR - 20251003_123045
```

### Email Sections

#### WHO EXECUTED
```
Name: John Smith
Email: john.smith@example.com
Auth Method: DECLARATION
Submission Time: 2025-10-03 12:30:45
Submission ID: 20251003_123045
Declaration Date: 2025-10-03
```

#### WHAT WAS EXECUTED
```
File Name: trading_sheet_oct2025.csv
Total Trades: 15
Accounts: 8

Buy Orders: 10
R 1,500,000.00

Sell Orders: 5
25,000.00 units
```

#### SUBMISSION OUTCOME (Success)
```
✅ Submission Outcome: SUCCESS
Group ID: 7FBF30C9-E8BB-45F0-98DC-B4453D179782
Final Status: COMPLETED_WITH_BUSINESS_ERRORS
Environment: UAT
System ID: 27

⚠️ 2 Trade(s) Failed
Trade 1: User 1919215 | Instrument 20
Reason: Duplicate request detected. Cannot process an instruction with the same amount within 2 seconds.

Trade 2: User 1919215 | Instrument 45
Reason: Insufficient funds in account
```

#### SUBMISSION OUTCOME (Failed)
```
⚠️ Submission Outcome: FAILED
Error Type: VALIDATION_FAILED
Error Message: Trading data failed validation checks

Validation Errors:
• Row 3: BUY orders must specify a positive Amount value
• Row 7: SELL orders must specify a positive Units value
• Row 12: ContractCode must follow UT.ZA.{ShareCode} format
```

## Implementation Details

### Core Function: `send_comprehensive_audit_email()`

Located in `app/email_sender.py`:

```python
def send_comprehensive_audit_email(
    submission_status: str,  # 'success', 'failed', 'error'
    trade_data: Optional[pd.DataFrame] = None,
    api_results: Optional[Dict[str, Any]] = None,
    error_details: Optional[Dict[str, Any]] = None,
    csv_filename: Optional[str] = None,
    csv_content: Optional[bytes] = None
) -> bool
```

### Integration Points

The audit email is triggered at multiple points:

#### 1. Validation Failure (lines 392-421)
```python
if not validation['valid']:
    error_details = {
        'error_type': 'VALIDATION_FAILED',
        'message': 'Trading data failed validation checks',
        'validation_errors': validation.get('errors', []),
        'validation_warnings': validation.get('warnings', []),
        'timestamp': datetime.now().isoformat()
    }
    send_comprehensive_audit_email(
        submission_status='failed',
        trade_data=parser.parsed_data,
        error_details=error_details,
        csv_filename=csv_filename,
        csv_content=csv_content
    )
```

#### 2. API Submission Failure (lines 410-436)
```python
if not submission_result['success']:
    error_details = {
        'error_type': 'API_SUBMISSION_FAILED',
        'message': submission_result.get('message', 'Unknown API error'),
        'api_response': submission_result,
        'timestamp': datetime.now().isoformat()
    }
    send_comprehensive_audit_email(
        submission_status='failed',
        trade_data=parser.parsed_data,
        error_details=error_details,
        csv_filename=csv_filename,
        csv_content=csv_content
    )
```

#### 3. Successful Execution (lines 564-610)
```python
# Build comprehensive API results including detailed trade results
audit_api_results = {
    'group_id': returned_group_id,
    'status': final_status,
    'environment': api_client.environment.upper(),
    'system_id': api_client.system_id,
    'submitted_at': results.get('submitted_at'),
    'trade_count': len(api_payload['valueTradeAllocationRequestDTOS']),
    'success_count': detailed['success_count'],
    'failed_count': detailed['failed_count'],
    'failed_trades': detailed['failed_trades']
}

send_comprehensive_audit_email(
    submission_status='success',
    trade_data=parser.parsed_data,
    api_results=audit_api_results,
    csv_filename=csv_filename,
    csv_content=csv_content
)
```

#### 4. Unexpected Errors (lines 612-639)
```python
except Exception as e:
    error_details = {
        'error_type': type(e).__name__,
        'message': str(e),
        'timestamp': datetime.now().isoformat()
    }
    send_comprehensive_audit_email(
        submission_status='error',
        trade_data=parser.parsed_data if parser.parsed_data is not None else None,
        error_details=error_details,
        csv_filename=csv_filename,
        csv_content=csv_content
    )
```

## Configuration

### Required Settings (.streamlit/secrets.toml)

```toml
[email_credentials]
email_address = "trading@easyequities.co.za"
app_password = "your-gmail-app-password"  # Generate from Google Account settings
notification_address = "trading-ops@easyequities.co.za"  # Receives all audit emails
```

### Optional Settings

```toml
[email_credentials]
smtp_server = "smtp.gmail.com"  # Auto-detected if not specified
smtp_port = 587  # Default: 587
```

## Authentication Evolution Path

The system is designed to seamlessly transition to more robust authentication:

### Phase 1: Declaration (Current)
- User enters name and email
- Declaration timestamp captured
- Simple but effective for audit

### Phase 2: OAuth/SSO (Future)
```python
# No changes to audit email function needed!
# Only update get_user_identity():
if 'user' in st.session_state and hasattr(st.session_state.user, 'email'):
    identity['name'] = st.session_state.user.name
    identity['email'] = st.session_state.user.email
    identity['auth_method'] = 'oauth'
    identity['user_id'] = st.session_state.user.id
```

### Phase 3: Enterprise SSO (Future)
```python
# LDAP/Active Directory integration
if 'ad_user' in st.session_state:
    identity['name'] = st.session_state.ad_user.display_name
    identity['email'] = st.session_state.ad_user.mail
    identity['auth_method'] = 'active_directory'
    identity['user_id'] = st.session_state.ad_user.sam_account_name
    identity['department'] = st.session_state.ad_user.department
```

## Benefits

### 1. Complete Traceability
- Every submission attempt is recorded
- WHO, WHAT, WHEN, and OUTCOME always captured
- No submissions can occur without audit trail

### 2. Regulatory Compliance
- Permanent email records
- CSV attachments preserve evidence
- Timestamps prove when actions occurred

### 3. Operational Excellence
- Failed submissions create learning opportunities
- Error patterns can be analyzed
- User behavior can be tracked for training needs

### 4. Debugging & Support
- Complete context for troubleshooting
- Original data files attached
- Error details included

### 5. Security
- All actions attributed to specific users
- Authentication method recorded
- Future-proof for SSO integration

## Testing

### Test Scenarios

1. **Successful Submission**: Upload valid CSV, execute, check audit email
2. **Validation Failure**: Upload invalid CSV (bad format), check failure email
3. **API Failure**: Test with invalid credentials, check error email
4. **Network Error**: Disconnect, attempt submission, check error email

### Verification Checklist

- [ ] Email received for successful submission
- [ ] Email received for validation failure
- [ ] Email received for API failure
- [ ] Email received for unexpected error
- [ ] CSV file attached to all emails
- [ ] User identity correctly captured
- [ ] Trade details accurate
- [ ] Failure reasons detailed
- [ ] Timestamps present
- [ ] Attachments readable

## Maintenance

### Adding New Authentication Methods

1. Update `get_user_identity()` in `app/email_sender.py`
2. Add new authentication check (OAuth, API key, etc.)
3. Set appropriate `auth_method` value
4. No changes needed to `send_comprehensive_audit_email()`

### Email Template Updates

Modify the HTML template in `send_comprehensive_audit_email()`:
- Styling: Lines 137-157
- WHO section: Lines 167-194
- WHAT section: Lines 197-234
- OUTCOME section: Lines 236-307

### Adding New Attachment Types

```python
# Add custom attachment
custom_part = MIMEText(custom_data, 'plain')
custom_part.add_header(
    'Content-Disposition',
    f'attachment; filename="custom_report_{submission_id}.txt"'
)
msg.attach(custom_part)
```

## Conclusion

The comprehensive audit email system ensures that **every trading submission** creates a permanent, detailed record. This system:
- Supports current declaration-based identity
- Ready for future OAuth/SSO integration
- Captures complete context for compliance
- Enables operational improvements
- Provides debugging capabilities

The architecture is **authentication-agnostic**, meaning it will continue to work seamlessly as the application evolves to more sophisticated authentication methods.
