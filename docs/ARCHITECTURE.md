# Trading Sheet Upload Application - Technical Architecture

## Overview

This document describes the technical architecture of the Trading Sheet Upload application for processing Unit Trust trades through the EasyEquities Trade Allocations Monitor API. The system implements a **file-based trading workflow** with comprehensive validation, asynchronous execution monitoring, audit trails, and API integration.

## Core Principles

1. **📁 File-Based Processing**: Excel and CSV trading sheets uploaded for batch processing
2. **✅ Declaration-First**: Mandatory accuracy declarations before data submission
3. **🔒 Secure Transmission**: Encrypted API communication for trade execution
4. **📋 Audit Compliance**: Complete transaction history and user accountability
5. **🎯 Validation-Driven**: Multi-layer validation before API submission
6. **📊 Batch Optimization**: Process multiple trades in single API calls
7. **🔄 Asynchronous Execution**: Real-time monitoring of trade execution status

## Architecture Flow

```
User Upload → Validation → Processing → Phase 1: Submit → Phase 2: Poll → Phase 3: Results
     ↓            ↓           ↓             ↓                ↓              ↓
   Excel/CSV   Format &    Transform    Trade          Monitor         Detailed
   Trading     Business    to API     Allocations     groupStatusID   Allocation
   Sheet       Rules       Payload    (Group ID)      (0,1,2)         Results
                                          ↓                ↓              ↓
                                     Kafka Events    MongoDB        Email &
                                                    Storage         Reports
```

## System Components

### 1. User Interface Layer

#### Declaration & Acceptance (`pages/1_Informed_Consent.py`)
- **Purpose**: Capture user declarations for audit compliance
- **Components**:
  - Digital signature capture
  - Terms acceptance checkboxes
  - Timestamp recording
  - Session initialization

#### Trading Sheet Upload (`app/main.py`)
- **Purpose**: File upload and initial validation
- **Features**:
  - Multi-format support (xlsx, xls, csv)
  - File size validation (max 10MB)
  - Format verification
  - Real-time validation feedback
  - Upload status tracking

#### Review & Execute (`pages/3_Declaration_and_Submit.py`)
- **Purpose**: Complete two-phase trade execution and monitoring
- **Phase 1 Components**:
  - Data table display with validation summary
  - API payload preview functionality
  - Trade execution dialog with confirmation
  - Real-time submission tracking
- **Phase 2 Components**:
  - Asynchronous status polling (5-second intervals)
  - Live status updates with business error detection
  - `groupStatusID` monitoring (0=incomplete, 1=success, 2=with errors)
  - Execution history with detailed results
- **Support Components**:
  - Debug & troubleshooting panel
  - Complete payload visibility
  - Business vs system error differentiation

### 2. Data Processing Layer

#### Trading Sheet Parser (`app/trading_sheet_parser.py`)
- **Purpose**: Extract and validate trading data
- **Supported Formats**:
  ```python
  parsers = {
      'xlsx': pd.read_excel,
      'xls': pd.read_excel,
      'csv': pd.read_csv
  }
  ```
- **Validation Steps**:
  - Column presence check (Units optional)
  - Data type validation
  - Business rule enforcement
  - Duplicate detection
  - Amount/Direction validation
  - ShareCode/ContractCode consistency

#### Data Validator
- **Required Fields**:
  - ShareCode (fund identifier)
  - ContractCode (UT.ZA.{ShareCode} format)
  - InstrumentID (positive integer)
  - Amount (positive decimal, 2 places)
  - Direction (BUY/SELL only)
  - UserID (numeric identifier)
  - TrustAccount (numeric account)
- **Optional Fields**:
  - Units (defaults to 0 for value-based trades)

### 3. API Integration Layer

#### Trade Allocations Client (`app/api/trade_client.py`)
- **Primary Endpoints**:
  ```python
  # Submit value-based trades
  POST /tradeallocations/monitored/order/createValueOrdersWithSystemIdentifier
  Base: https://tradeallocationsapi.purple-uat.easyequities.io
  
  # Monitor execution status
  GET /tradeGroupStatus/{groupID}
  Base: https://trade-allocations-monitor.purple-uat.easyequities.io
  
  # Get detailed results
  GET /trade-monitor/allocation/all/{groupID}
  Base: https://trade-allocations-monitor.purple-uat.easyequities.io
  ```

#### Data Mapper (`app/api/trade_mapper.py`)
- **Purpose**: Transform CSV data to API payload format
- **Key Mappings**:
  - Direction → trustAccountActionId (7=BUY, 8=SELL)
  - Direction → costCalculationType (1=BUY, 2=SELL)
  - TrustAccount → trustAccountID
  - Generate unique Group ID (UUID)
  - Create unique transaction references

#### Authentication & Security
- **Bearer Token**: Secure storage in `.streamlit/secrets.toml`
- **TLS Encryption**: All API communication over HTTPS
- **System Identifier**: Unique ID (27) for this system
- **Timeout Handling**: 30-second API timeout
- **Retry Logic**: Up to 3 attempts for failed requests
- **Polling Duration**: Maximum 5 minutes with 5-second intervals

### 4. Session Management

#### State Persistence
- **Session State Variables**:
  ```python
  session_state = {
      # File upload state
      'file_uploaded': bool,
      'uploaded_file': UploadedFile,
      'trading_parser': TradingSheetParser,
      
      # Consent state
      'consent_given': bool,
      'consent_name': str,
      'consent_timestamp': datetime,
      
      # API state
      'api_payload': dict,
      'trade_group_id': str,
      'trade_execution_results': dict,
      'trade_execution_history': list,
      
      # UI state
      'show_confirmation': bool,
      'executing_trades': bool,
      'last_api_request': dict,
      'last_api_response': dict
  }
  ```

### 5. Notification System

#### Email Service (`app/email_sender.py`)
- **Purpose**: Send trade execution confirmations
- **Features**:
  - Group ID reference for tracking
  - Trade summary with execution results
  - Success/error status breakdown
  - JSON report as attachment
  - Error details for failed trades
  - Timestamp and environment info

#### PDF Generation (`app/pdf_generator.py`)
- **Trade Reports**: Formatted execution summaries
- **Audit Documents**: Declaration records with timestamps
- **Reference Numbers**: Group IDs for tracking

## Data Flow

### Upload Flow
1. **User Declaration** → Accept terms and provide digital signature
2. **File Selection** → Choose Excel/CSV file
3. **Upload & Validate** → Check format and business rules
4. **Preview Data** → Display parsed trades with validation
5. **Final Review** → Confirm trades before execution

### Execution Flow

#### **Pre-Execution**
1. **Parse File** → Extract trading data from CSV/Excel
2. **Validate Data** → Apply comprehensive business rules
3. **Transform** → Convert to API payload format
4. **Preview Payload** → Show complete API request structure

#### **Phase 1: Trade Submission**
5. **Submit Batch** → POST to `/createValueOrdersWithSystemIdentifier`
6. **Receive Group ID** → Store UUID for tracking (e.g., `1AF0B1EE-543F-4726-AC2C-FD44D5AC5868`)
7. **Confirm Submission** → Display success and Group ID

#### **Phase 2: Execution Monitoring**
8. **Start Polling** → GET `/tradeGroupStatus/{groupID}` every 5 seconds
9. **Monitor Status** → Check `groupStatusID` for completion
10. **Handle Business Errors** → Distinguish insufficient funds from system errors
11. **Retrieve Details** → GET `/trade-monitor/allocation/all/{groupID}` on completion

#### **Phase 3: Results & Notification**
12. **Display Results** → Show execution summary with success/failure metrics
13. **Generate Reports** → Create downloadable execution reports
14. **Send Email** → Automated confirmation with Group ID and results

## Asynchronous Processing Architecture

### Multi-Phase Trade Execution Pattern
```
Phase 1: Submit → Group ID → Phase 2: Poll → Status → Phase 3: Results
    ↓                         ↓                      ↓
Immediate            Real-time              Detailed
Confirmation         Monitoring             Reporting
```

### Backend Integration (EasyEquities Infrastructure)

#### **Kafka Event Stream**
- **TradeMonitorMessage**: Individual trade status updates
- **TradeAllocationGroupCompleteMessage**: Batch completion events
- **Real-time Aggregation**: 1-second intervals for status updates

#### **MongoDB Storage**
- **TradeGroupStatus Collection**: Group-level status tracking
  ```
  {
    "groupID": "UUID",
    "groupStatusID": 0|1|2,
    "totalSuccess": int,
    "totalFailed": int,
    "totalTradesInGroup": int,
    "groupStatus": "Complete with Failures"
  }
  ```
- **Individual Trade Records**: Detailed allocation results
- **Query Interface**: Supports polling for real-time updates

#### **Business Logic Processing**
- **Status Aggregation**: Tracks individual trade completions
- **Terminal State Detection**: `groupStatusID` 1 or 2 = complete
- **Business Error Handling**: Insufficient funds, account restrictions
- **Audit Trail**: Complete transaction history with timestamps

## File Structure

```
trading-sheet-applet/
├── app/
│   ├── main.py                        # Upload interface
│   ├── pages/
│   │   ├── 1_Informed_Consent.py     # Declaration page
│   │   └── 3_Declaration_and_Submit.py # Review & execute
│   ├── api/
│   │   ├── trade_client.py           # API client
│   │   └── trade_mapper.py           # Data transformer
│   ├── components/
│   │   ├── sidebar.py                # Navigation
│   │   └── submission.py             # State handler
│   ├── trading_sheet_parser.py       # CSV/Excel parser
│   ├── email_sender.py               # Notifications
│   ├── pdf_generator.py              # Reports
│   └── utils.py                      # Utilities
├── docs/
│   ├── API_Integration_Guide.md      # API details
│   └── API_Call_Flow_Verification.md # Flow verification
├── postman/
│   └── TradeAllocationsMonitor.postman_collection.json
├── assets/
│   └── logos/                        # Branding
└── .streamlit/
    └── secrets.toml                  # API credentials
```

## Configuration

### API Configuration
```toml
[trade_api]
environment = "uat"  # uat|qa|prod
uat_base_url = "https://tradeallocationsapi.purple-uat.easyequities.io"
uat_monitor_url = "https://trade-allocations-monitor.purple-uat.easyequities.io"
api_key = "bearer-token"
system_identifier_id = 27
api_timeout = 30
max_retry_attempts = 3
status_polling_interval = 5
max_polling_duration = 300
```

### Environment Settings
```toml
[environment]
mode = "production"  # production|staging|development
debug = false
max_file_size_mb = 10
allowed_extensions = ["xlsx", "xls", "csv"]
```

## Security Considerations

1. **Input Validation**: Comprehensive sanitization of all inputs
2. **File Security**: Size limits and format verification
3. **API Security**: Bearer token authentication, HTTPS only
4. **Audit Logging**: Complete transaction trail with timestamps
5. **Data Privacy**: No permanent file storage, memory-only processing
6. **Error Handling**: Sanitized error messages to prevent data leaks

## Error Handling

### Validation Errors
- Display specific field errors with row numbers
- Highlight problematic data points
- Provide correction guidance
- Support optional Units column

### API Errors
- Retry logic with exponential backoff
- User-friendly error messages
- Detailed troubleshooting tips
- Debug panel for technical details

### System Errors
- Graceful degradation
- Comprehensive error logging
- User notification with Group ID reference
- Fallback to manual retry options

## Performance Optimization

### **Multi-Phase Efficiency**
1. **Batch Processing**: Group all trades in single API call (Phase 1)
2. **Async Polling**: Non-blocking status monitoring (Phase 2)
3. **Intelligent Termination**: Stop polling on terminal states (1 or 2)
4. **Session State Management**: Efficient state persistence across phases
5. **Connection Pooling**: Reuse API connections across polling cycles

### **Real-time Updates**
6. **Progress Indicators**: Live UI updates during all phases
7. **Status Streaming**: 5-second polling intervals
8. **Error Detection**: Immediate business vs system error identification
9. **Payload Caching**: Store API requests/responses for debugging
10. **Resource Management**: Automatic cleanup after completion

## Monitoring & Observability

### **Phase-by-Phase Tracking**
1. **Submission Monitoring**: Track Phase 1 success rates and Group ID generation
2. **Polling Observability**: Monitor Phase 2 status checks and response times
3. **Business Error Analytics**: Track insufficient funds and other business rule violations
4. **System Error Detection**: Identify API failures, timeouts, and connection issues

### **Debug & Transparency Tools**
5. **Payload Visibility**: Complete API request/response inspection
6. **Real-time Status Display**: Live updates during polling
7. **Execution History**: Historical tracking with Group IDs
8. **Debug Panel**: Technical details for troubleshooting
9. **Audit Trail**: Complete transaction lifecycle tracking

## Future Enhancements

1. **Webhook Support**: Replace polling with push notifications
2. **Template Generation**: Download pre-formatted sheets
3. **Historical Analytics**: Trading pattern insights
4. **Multi-user Support**: Team-based workflows
5. **Advanced Validation**: Real-time validation as user types
6. **Bulk Operations**: Support for multiple file uploads

## Development Guidelines

1. **Type Safety**: Use type hints for all functions
2. **Error Messages**: Clear, actionable user feedback
3. **Logging**: Comprehensive audit trail
4. **Testing**: Unit tests for validators and parsers
5. **Documentation**: Inline comments for complex logic
6. **Code Review**: Peer review for all API integrations