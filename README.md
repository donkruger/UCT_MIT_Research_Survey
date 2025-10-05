# Trading Sheet Upload Application

A professional trading operations application for processing Unit Trust (UT) trades through the EasyEquities Accounts Processor API.

## 🎯 Purpose

This application facilitates the secure upload and processing of Unit Trust trading sheets through the **EasyEquities Trade Allocations Monitor API**. It implements a **complete two-phase asynchronous trading workflow**:

### 🚀 **Phase 1: Trade Submission** 
- Submit trades via `/createValueOrdersWithSystemIdentifier`
- Receive Group ID for tracking
- Complete payload transparency and debugging

### 🔄 **Phase 2: Execution Monitoring**
- Real-time polling of `/tradeGroupStatus/{groupID}`
- Detailed failure feedback via `/trade-monitor/allocation/all/{groupID}`
- Intelligent handling of business vs system errors
- Individual trade-level success/failure reporting
- Comprehensive execution reporting and email notifications

### 🎯 **Key Capabilities**
- Streamlined trade submission workflow with real-time status tracking
- Comprehensive data validation and compliance checks
- Complete audit trail for all trading operations
- Advanced business error handling (insufficient funds, etc.)
- Integration with Kafka-based Trade Allocations Monitor service

## Features

### 🏗️ **Multi-Step API Integration**
- **Phase 1**: Trade submission with immediate confirmation
- **Phase 2**: Asynchronous polling with real-time status updates
- **Smart Error Handling**: Distinguishes system errors from business rule violations

### 💼 **Trading Operations**
- 📁 **File Upload Interface**: Support for Excel (.xlsx, .xls) and CSV formats
- ✅ **Declaration & Compliance**: Mandatory accuracy declarations for audit purposes
- 🔒 **Secure Processing**: Bearer token authentication and HTTPS encryption
- 📊 **Data Preview & Validation**: Review and validate trading data before submission
- 📈 **Batch Processing**: Upload multiple Unit Trust trades in a single batch

### 🔄 **Execution Monitoring**
- **Real-time Polling**: 5-second intervals with 5-minute timeout
- **Status Tracking**: Monitor `groupStatusID` (0=incomplete, 1=success, 2=with errors)
- **Detailed Failure Feedback**: Individual trade-level failure reasons and explanations
- **Business Error Handling**: Proper handling of insufficient funds, account restrictions
- **Success/Failure Metrics**: Real-time counts of successful, failed, and pending trades
- **Complete Transparency**: Full payload visibility and allocation details for debugging

### 📋 **Audit & Reporting**
- **Comprehensive Audit Trail**: Email sent for ALL submissions (success, failure, error)
- **Who Executed**: User identity captured from declaration/authentication system
- **What Was Executed**: Complete trade details with CSV attachment
- **Submission Outcomes**: Success, failure, or error states with detailed reasons
- **Execution History**: Track all submissions with Group IDs
- **Authentication-Ready**: Audit system supports future OAuth/SSO integration
- **Debug Tools**: Built-in diagnostics and troubleshooting panel
- 🎨 **Modern UI**: Professional interface with EasyEquities branding

### 🛡️ **Security Architecture**
- **⚿ User Authentication**: Password-based authentication with bcrypt hashing (MVP implementation)
- **🔒 UT-Only Protection**: Enforces Unit Trust-only trading by blocking non-UT `ContractCode` values
- **🔐 Fail-Safe Defaults**: Protection is enabled by default and requires explicit configuration to disable
- **📋 Comprehensive Auditing**: All validation attempts and security events are logged
- **🛡️ Input Sanitization**: Protects against injection attacks and malicious input
- **⚙️ Environment Hardening**: Production environments enforce the strictest security settings
- **🔑 Session Management**: 60-minute session timeout with 30-minute inactivity timeout
- **🚫 Rate Limiting**: Brute force protection (5 failed attempts = 15-minute lockout)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd trading-sheet-applet
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API settings by creating `.streamlit/secrets.toml`:
```toml
# Authentication Configuration (MVP)
[auth]
provider = "secrets"  # MVP: secrets.toml based authentication
session_timeout_minutes = 60
session_inactivity_timeout_minutes = 30
max_login_attempts = 5
lockout_duration_minutes = 15

[users.admin]
"user@example.com" = {name = "User Name", password_hash = "$2b$12$...", role = "admin", enabled = true}
# Generate password hash: python3 -c "import bcrypt; print(bcrypt.hashpw(b'YourPassword', bcrypt.gensalt()).decode())"

[trade_api]
environment = "uat"  # Options: uat, qa, prod
uat_base_url = "https://tradeallocationsapi.purple-uat.easyequities.io"
uat_monitor_url = "https://trade-allocations-monitor.purple-uat.easyequities.io"
api_key = "your-api-key-here"  # Bearer token for authentication
system_identifier_id = 27  # Your system identifier
api_timeout = 30
max_retry_attempts = 3
status_polling_interval = 5  # seconds
max_polling_duration = 300  # seconds (5 minutes)

[email_credentials]
email_address = "trading@easyequities.co.za"
app_password = "your-app-password"
notification_address = "trading-ops@easyequities.co.za"
```

4. Run the application:
```bash
streamlit run app/main.py
# OR use the startup script:
./run.sh
```

## 📋 Trading Sheet Format

### Required Columns for Unit Trust Trades

Your trading sheet must include these columns:

1. **ShareCode** - Fund share code identifier (e.g., NGWINT)
2. **ContractCode** - Full contract identifier (must start with `UT.ZA`)
3. **InstrumentID** - Numeric instrument identifier (e.g., 4257)
4. **Amount** - Trade amount in ZAR (2 decimal places) - **Required for BUY orders**
5. **Units** - Number of units to trade (up to 8 decimal places) - **Required for SELL orders**
6. **Direction** - Trade direction (BUY or SELL only)
7. **UserID** - User identifier (numeric)
8. **TrustAccount** - Trust account number (numeric)

**Note**: The application enforces specific business rules for `Amount` and `Units`:
- **BUY orders** are value-based and **must** specify a positive `Amount`. `Units` should be empty or 0.
- **SELL orders** are unit-based and **must** specify a positive `Units`. `Amount` should be empty or 0.

### Supported File Formats

- **Excel Files**: .xlsx, .xls
- **CSV Files**: .csv (comma-delimited)

### Data Validation Rules

- **UT-Only Protection**: All trades must be Unit Trusts (ContractCode must start with `UT.ZA`)
- **BUY Orders**: Must have a positive `Amount` specified.
- **SELL Orders**: Must have a positive `Units` specified.
- All other required columns must be populated for each trade
- ShareCode must match approved fund list
- ContractCode must follow `UT.ZA.{ShareCode}` format
- InstrumentID must be valid positive integer
- Direction must be either BUY or SELL (case sensitive)
- UserID and TrustAccount must be valid active accounts
- No duplicate trades allowed in the same batch

## 🔄 Application Workflow

### 1. User Authentication (Login)
- **Login Required**: All users must authenticate before accessing the application
- Enter authorized email address
- Enter password (with show/hide toggle for visibility)
- System validates credentials using bcrypt password hashing
- **Security Features**:
  - Rate limiting: 5 failed attempts = 15-minute lockout
  - Session timeout: 60 minutes (absolute) or 30 minutes (inactivity)
  - All login attempts logged for audit
- Upon successful login, user identity captured for audit trail

### 2. Declaration & Acceptance
- User identity auto-populated from authenticated session (read-only)
- User confirms data accuracy
- Accepts responsibility for trade execution
- Provides digital signature for audit trail

### 3. Trading Sheet Upload
- Select and upload trading file
- System validates file format
- Preview data (when available)
- Confirm readiness for processing

### 4. Review & Execute (Two-Phase Process)

#### **Phase 1: Trade Submission**
- Final review of trading data with validation summary
- Preview complete API payload before execution
- Declaration confirmation with digital signature
- Submit to Trade Allocations API: `/createValueOrdersWithSystemIdentifier`
- Receive Group ID confirmation

#### **Phase 2: Execution Monitoring**
- Real-time polling of `/tradeGroupStatus/{groupID}` every 5 seconds
- Live status updates with progress indicators
- Intelligent business error detection (insufficient funds, etc.)
- **Enhanced Failure Feedback**: Automatic retrieval of detailed trade allocation results
- **Individual Trade Status**: See exact failure reasons for each failed trade
  - Duplicate request detection
  - Insufficient funds
  - Account restrictions
  - Invalid instruments
  - Market hours violations
- Complete execution summary with success/failure breakdown
- Email confirmation and downloadable reports

## Project Structure

```
trading-sheet-applet/
├── app/
│   ├── main.py                    # Main trading sheet upload page
│   ├── pages/
│   │   ├── 1_Informed_Consent.py # Declaration & Acceptance
│   │   └── 3_Declaration_and_Submit.py # Review, Execute & Monitor
│   ├── api/
│   │   ├── trade_client.py      # Trade Allocations API client
│   │   └── trade_mapper.py      # CSV to API payload mapper
│   ├── components/
│   │   ├── sidebar.py           # Navigation with progress tracker
│   │   └── submission.py        # Submission state handler
│   ├── trading_sheet_parser.py  # CSV/Excel parser & validator
│   ├── email_sender.py          # Trade confirmation emails
│   ├── pdf_generator.py         # Trade report generation
│   └── utils.py                 # Utilities
├── assets/
│   └── logos/                   # EasyEquities branding
├── docs/
│   ├── API_Integration_Guide.md # API integration details
│   ├── API_Call_Flow_Verification.md # API flow verification
│   ├── ENHANCED_POLLING_DOCUMENTATION.md # Detailed failure feedback
│   ├── UT_ONLY_PROTECTION.md # Security architecture
│   └── POLLING_EXPLANATION.md # Polling mechanics
├── requirements.txt              # Python dependencies
├── API_INTEGRATION.md           # API specifications
├── ARCHITECTURE.md              # Technical documentation
├── QUICKSTART.md               # Quick start guide
└── README.md                   # This file
```

## Configuration

### Multi-Phase API Integration

The application implements a **two-phase asynchronous trading workflow**:

#### **🚀 Phase 1: Trade Submission**
```
POST /tradeallocations/monitored/order/createValueOrdersWithSystemIdentifier
Base: https://tradeallocationsapi.purple-uat.easyequities.io
```
- Submits batch of value-based trades
- Returns Group ID for tracking
- Complete payload transparency
- Immediate confirmation

#### **🔄 Phase 2: Execution Monitoring** 
```
GET /tradeGroupStatus/{groupID}
Base: https://trade-allocations-monitor.purple-uat.easyequities.io  
```
- Polls every 5 seconds for up to 5 minutes
- Checks `groupStatusID` (0=incomplete, 1=success, 2=with errors)
- Handles business errors intelligently
- Provides detailed execution summary

#### **📊 Enhanced Polling: Detailed Trade Results**
```
GET /trade-monitor/allocation/all/{groupID}
Base: https://trade-allocations-monitor.purple-uat.easyequities.io
```
After polling completes, the application automatically fetches detailed allocation data:
- **Individual Trade Status**: Maps `allocationStatusId` (0=pending, 3=failed, 4=success)
- **Specific Failure Reasons**: Extracts and parses detailed error messages
- **Transaction Details**: User ID, Instrument ID, amounts, account numbers
- **Success Tracking**: Transaction IDs for completed trades
- **Comprehensive Metrics**: Real-time counts of successful/failed/pending trades

**Example Failure Feedback:**
```
❌ Failed Trade 1:
   User ID: 1919215
   Instrument ID: 20
   Amount: R 100.00
   Trust Account: 8726095
   Failure Reason: Duplicate request detected. Cannot process 
                   an instruction with the same amount within 2 seconds.
```

This enhancement provides complete transparency into why specific trades fail, enabling:
- Faster problem resolution
- Better compliance and audit trails
- Self-service error correction
- Reduced support burden

Configure all endpoints in `.streamlit/secrets.toml` as shown in Quick Start section.

### Security Configuration

Configure security settings in `.streamlit/secrets.toml`:
```toml
[trade_protection]
# Enable/disable UT-only protection (fail-safe default is true)
block_non_ut_trades = true
# Specify supported contract prefixes
supported_contract_prefixes = ["UT.ZA"]
# Set protection mode: "strict" (block) or "audit_warn" (allow with log)
protection_mode = "strict"
```

### Email Notifications & Audit Trail

The application sends comprehensive audit trail emails for ALL submissions:

```toml
[email_credentials]
smtp_server = "smtp.gmail.com"
smtp_port = 587
email_address = "trading@easyequities.co.za"
app_password = "your-gmail-app-password"
notification_address = "trading-ops@easyequities.co.za"  # Receives all audit emails
```

**Audit Email Features:**
- **WHO Executed**: Captured from authenticated user session (name, email, role, login timestamp)
- **WHAT Was Executed**: Complete trade details, file names, amounts
- **WHEN**: Precise timestamps for all actions
- **OUTCOME**: Success, failure, or error with detailed reasons
- **ATTACHMENTS**: 
  - Original CSV file
  - API execution results (JSON)
  - Error details (if applicable)

**Email Sent For:**
- ✅ **Successful submissions** - with complete trade execution details
- ⚠️ **Failed submissions** - validation errors, API failures
- ❌ **Error conditions** - unexpected errors with debug information

**Authentication Design:**
The audit system works seamlessly with multiple authentication methods:
- **Current (MVP)**: Password-based authentication (bcrypt, secrets.toml)
- **Future**: OAuth/SSO (Google, Microsoft, etc.) - swap with one line change
- **Future**: API key authentication
- **Future**: LDAP/Active Directory

### Environment Settings

Switch between production and staging:
```toml
[environment]
mode = "production"  # or "staging"
debug = false
log_level = "INFO"
```

### User Authentication & Management (MVP)

The application implements **password-based authentication** with industry-standard security features:

#### Authentication Architecture

**Provider Pattern (Swappable):**
- Current: `SecretsAuthProvider` - credentials stored in `secrets.toml` (MVP)
- Future: Switch to OAuth2, LDAP, or database authentication by changing one line
- Zero code changes required to swap authentication providers

**Security Features:**
- **bcrypt Password Hashing**: Industry-standard password hashing with automatic salting
- **Session Management**: 
  - 60-minute absolute timeout
  - 30-minute inactivity timeout
  - Secure session tokens
- **Rate Limiting**: 
  - 5 failed login attempts = 15-minute lockout
  - Countdown timer displayed during lockout
- **Audit Logging**: All authentication attempts logged
- **Role-Based Access Control**: Support for admin, trader, and viewer roles

#### Adding Users

**Generate password hash:**
```bash
python3 -c "import bcrypt; print(bcrypt.hashpw(b'YourPassword', bcrypt.gensalt()).decode())"
```

**Add to `.streamlit/secrets.toml`:**
```toml
[users.admin]
"user@example.com" = {name = "User Name", password_hash = "$2b$12$...", role = "admin", enabled = true}
```

**User Roles:**
- **admin**: Full access to all features
- **trader**: Can execute trades and view history
- **viewer**: Read-only access (future use)

#### Authentication Integration

The authentication system seamlessly integrates with the audit trail:
- User identity automatically captured upon login
- All trades attributed to authenticated user
- Audit emails include:
  - User's full name
  - User's email address
  - User's role
  - Login timestamp
  - Authentication method

#### Future Migration

To switch to enterprise authentication (e.g., Google OAuth):
1. Implement `OAuth2AuthProvider` class
2. Change `secrets.toml`: `provider = "oauth"`
3. **Zero changes** to application code required ✓

**Documentation:**
- Full design: `docs/user_management_solution_design.md`
- Implementation summary: `docs/AUTHENTICATION_IMPLEMENTATION_SUMMARY.md`

## Security & Compliance

- **User Authentication**: Password-based authentication with bcrypt hashing (MVP implementation)
- **Session Security**: 60-minute timeout, 30-minute inactivity timeout, secure tokens
- **Rate Limiting**: Brute force protection (5 failed attempts = 15-minute lockout)
- **Data Encryption**: All trading data encrypted during transmission
- **Access Control**: Multi-level authentication (user login + API access)
- **Comprehensive Audit Trail**: Email sent for every submission attempt
- **Complete Audit Logging**: WHO executed, WHAT was executed, WHEN, and OUTCOME
- **CSV Attachment**: Original trading file attached to all audit emails
- **Compliance Checks**: Automated validation against trading rules
- **Data Retention**: Compliance with regulatory requirements
- **Future-Ready**: Clean migration path to enterprise SSO/OAuth integration

### Audit Trail Architecture

The application implements a comprehensive audit system that ensures **complete traceability** of all trading operations:

#### 1. Identity Capture (WHO)
- **Primary Method**: Password authentication (bcrypt-based)
  - User authenticates with email and password
  - Identity captured automatically from authenticated session
  - Full name, email, role, and login timestamp recorded
- **Authentication Method Tracked**: password, OAuth, SSO, API key, etc.
- **Future-Ready**: Seamless migration path to enterprise SSO/OAuth

#### 2. Action Capture (WHAT)
- Complete trading data (all trades in batch)
- CSV filename and upload timestamp
- Trade counts (buy/sell, amounts, units)
- Unique accounts and instruments involved

#### 3. Outcome Tracking (RESULT)
- ✅ **Success**: Group ID, API status, individual trade results
- ⚠️ **Failure**: Validation errors, API errors, specific failure reasons
- ❌ **Error**: Exception details, stack traces, debugging information

#### 4. Evidence Preservation
- **CSV Attachment**: Original uploaded file
- **JSON Reports**: API responses, execution summaries
- **Email Archive**: Permanent record sent to compliance team

This architecture ensures that **every trading submission** (successful or failed) generates a complete, auditable record that can be:
- Retrieved for compliance audits
- Used for debugging and troubleshooting
- Analyzed for operational improvements
- Presented as evidence of proper procedures

## Error Handling

### System vs Business Errors

The application intelligently differentiates between:

#### **🔴 System Errors** (Technical Issues)
- API connection failures
- Authentication problems
- Network timeouts
- Invalid payloads

#### **🟡 Business Errors** (Expected Outcomes)
The application now provides **detailed failure feedback** for each trade, including:
- **Insufficient Funds**: Specific account balance issues
- **Duplicate Requests**: Same amount within 2-second window
- **Invalid Instruments**: Trading not permitted for specific securities
- **Account Restrictions**: Compliance or regulatory blocks
- **Market Hours**: Trading outside allowed hours
- **Price Limits**: Orders exceeding allowed ranges

Each failed trade displays:
- User and instrument details
- Exact failure reason from the API
- Account and amount information
- Suggested corrective actions

### Common Issues

1. **Authentication Issues**
   - **Invalid Credentials**: Verify email and password are correct
   - **Account Locked**: After 5 failed attempts, wait 15 minutes or contact admin
   - **Session Expired**: Re-login if session times out (60 min absolute, 30 min inactivity)
   - **Password Not Working**: Ensure password hash in `secrets.toml` is correct bcrypt format
   - **Adding Users**: Use bcrypt to generate password hash, add to `[users.admin]` section

2. **File Upload Issues**
   - Ensure file is .xlsx, .xls, or .csv
   - Check column headers match exactly (case-sensitive)
   - Units column is optional for value-based trades

3. **API Integration Issues**
   - Ensure VPN connection for UAT environment
   - Verify Bearer token in `.streamlit/secrets.toml`
   - Check system_identifier_id is set to 27
   - Use "Test API Configuration" for diagnostics

4. **Execution Monitoring**
   - Status 2 = "Complete with Failures" is normal for business errors
   - Polling timeout after 5 minutes indicates slow processing
   - **View Detailed Results**: Expand "Detailed Trade Results" to see specific failure reasons
   - **Execution History**: Recent executions now show individual failure details
   - Check Debug panel for detailed API responses and raw allocation data

## Support

### Technical Support
- **Email**: trading@easyequities.co.za
- **Phone**: Trading Desk (business hours)
- **Include**: Group ID, error messages, and timestamps

### Documentation
- **API Integration**: [API_INTEGRATION.md](API_INTEGRATION.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Quick Setup**: [QUICKSTART.md](QUICKSTART.md)
- **User Authentication (MVP)**: [docs/user_management_solution_design.md](docs/user_management_solution_design.md)
- **Authentication Implementation**: [docs/AUTHENTICATION_IMPLEMENTATION_SUMMARY.md](docs/AUTHENTICATION_IMPLEMENTATION_SUMMARY.md)
- **Polling Details**: [docs/POLLING_EXPLANATION.md](docs/POLLING_EXPLANATION.md)
- **Enhanced Polling with Failure Feedback**: [docs/ENHANCED_POLLING_DOCUMENTATION.md](docs/ENHANCED_POLLING_DOCUMENTATION.md)
- **Comprehensive Audit Email System**: [docs/AUDIT_EMAIL_SYSTEM.md](docs/AUDIT_EMAIL_SYSTEM.md)
- **API Verification**: [docs/API_Call_Flow_Verification.md](docs/API_Call_Flow_Verification.md)
- **UT-Only Protection**: [docs/UT_ONLY_PROTECTION.md](docs/UT_ONLY_PROTECTION.md)

### Debug Resources
- **Postman Collection**: [postman/TradeAllocationsMonitor.postman_collection.json](postman/TradeAllocationsMonitor.postman_collection.json)
- **Built-in Debug Panel**: Available in app under "Debug & Support" tab
- **Sample CSV**: [docs/CSV_Upload_Convention.csv](docs/CSV_Upload_Convention.csv)

## Development

### Testing Environment

Use staging environment for testing:
```toml
[environment]
mode = "staging"
test_mode = true
skip_api_calls = false
```

### Data Structure Extensions

The application is designed to accommodate future data structure updates. Trading sheet parsers can be extended in `app/data/` when specifications are finalized.

## License

This application is proprietary software of EasyEquities for internal trading operations use only.