# Quick Start Guide - Trading Sheet Upload

## 🚀 Get Started in 3 Minutes

### 1. Install & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app/main.py
# OR use the startup script:
./run.sh
```

The application opens at `http://localhost:8501`

### 2. Configure API Access (IMPORTANT)

Create `.streamlit/secrets.toml`:
```toml
[trade_api]
# Environment (UAT requires VPN connection)
environment = "uat"
uat_base_url = "https://tradeallocationsapi.purple-uat.easyequities.io"
uat_monitor_url = "https://trade-allocations-monitor.purple-uat.easyequities.io"

# Authentication (REQUIRED - obtain from API team)
api_key = "your-bearer-token-here"

# System settings
system_identifier_id = 27
api_timeout = 30
status_polling_interval = 5
max_polling_duration = 300

[email_credentials]
email_address = "trading@easyequities.co.za"
app_password = "xxxx-xxxx-xxxx-xxxx"
notification_address = "trading-ops@easyequities.co.za"
```

**🔑 Critical Setup Requirements:**
- **VPN Connection**: Required for UAT environment access
- **Bearer Token**: Must be obtained from EasyEquities API team
- **System ID**: Fixed at 27 for this application

### 3. Complete Trading Process

#### **Step 1: Declaration & Consent**
1. Navigate to "Informed Consent" page
2. Read terms and conditions
3. Provide digital signature
4. Accept processing authorization

#### **Step 2: Upload Trading Sheet**
1. Go to main upload page
2. Select Excel (.xlsx) or CSV file
3. Review validation results
4. Address any errors if present

#### **Step 3: Review & Execute (Three Phases)**

**Phase 1: Submission**
- Review trades in data table
- Click "🔍 Preview API Payload" to inspect request
- Click "🚀 Execute Trades" → Confirm execution
- ✅ Receive Group ID (e.g., `1AF0B1EE-543F-4726-AC2C-FD44D5AC5868`)

**Phase 2: Monitoring**
- Automatic polling starts: "🔍 Polling for status of Group ID"
- Real-time updates every 5 seconds
- Status tracking: "Status: Processing (ID: 0)" → "Complete with Failures (ID: 2)"
- Business error detection for insufficient funds

**Phase 3: Results**
- Execution summary with success/failure breakdown
- Download PDF report
- Email confirmation with Group ID

---

## 📁 Trading Sheet Format

### Required Columns

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| **ShareCode** | Yes | Fund share code | NGWINT |
| **ContractCode** | Yes | Full contract identifier | UT.ZA.NGWINT |
| **InstrumentID** | Yes | Numeric instrument ID | 4257 |
| **Amount** | Yes | Trade amount in ZAR | 1000.12 |
| **Units** | No | Number of units (defaults to 0) | 0 |
| **Direction** | Yes | BUY or SELL | BUY |
| **UserID** | Yes | User identifier | 807686 |
| **TrustAccount** | Yes | Trust account number | 123456 |

**💡 Note**: Units column is optional for value-based trades and will default to 0.

### Sample CSV Format
```csv
ShareCode,ContractCode,InstrumentID,Amount,Direction,UserID,TrustAccount
NGWINT,UT.ZA.NGWINT,4257,1000.12,BUY,807686,123456
NGWINT,UT.ZA.NGWINT,4257,500.50,SELL,807686,123456
```

---

## 📊 Three-Phase Execution Workflow

### 🚀 **Phase 1: Trade Submission**
1. **Payload Generation**: CSV data → API format
2. **Submission**: POST to `/createValueOrdersWithSystemIdentifier`
3. **Confirmation**: Receive Group ID
4. **Status**: "✅ Orders submitted successfully!"

### 🔄 **Phase 2: Execution Monitoring**  
1. **Polling Start**: "🔍 Polling for status of Group ID: `{id}`"
2. **Status Updates**: Real-time monitoring every 5 seconds
3. **Business Error Detection**: Handle insufficient funds intelligently
4. **Completion**: Stop on `groupStatusID: 1` or `2`

### 📊 **Phase 3: Results Processing**
1. **Results Retrieval**: Fetch detailed allocation data
2. **Summary Display**: Success/failure metrics
3. **Error Explanation**: Business vs system error differentiation
4. **Reporting**: Email confirmation and downloadable reports

---

## ✅ Status Interpretation Guide

### **Phase 2 Status Values**

| groupStatusID | Meaning | Application Response |
|---------------|---------|---------------------|
| **0** | Processing | 🔄 Continue polling |
| **1** | All Success | 🎉 "All Trades Executed Successfully!" |
| **2** | With Failures | ⚠️ "Execution Complete - Some Trades Failed" |

### **Business vs System Errors**

#### **✅ Expected Business Errors** (Status 2)
- **Insufficient Funds**: Normal when account balance is low
- **Account Restrictions**: User account limitations
- **Invalid Instruments**: Instrument not available for trading
- **Market Hours**: Trading outside allowed hours

#### **❌ System Errors** (Connection/Auth)
- **VPN Required**: "Could not connect to API server"
- **Authentication**: HTTP 401 - Invalid Bearer token
- **Validation**: HTTP 422 - Invalid payload structure

---

## 🆘 Troubleshooting

### **Phase 1 Issues (Submission)**

**"Could not connect to API server"**
1. ✅ **Connect to VPN** (required for UAT)
2. ✅ **Verify Bearer token** in secrets.toml
3. ✅ **Test API Configuration** button

**"Submission Failed"**
1. Check payload structure with "Preview API Payload"
2. Verify all required CSV columns present
3. Ensure Amount values are positive

### **Phase 2 Issues (Polling)**

**"No polling visible"**
1. Check for misplaced `st.stop()` statements
2. Verify execution continues after submission success
3. Look for "Step 4/4: Polling for final trade status..."

**"Status stays at 0"**
1. Normal for up to 5 minutes
2. Backend processing through Kafka → MongoDB
3. Check if Group ID format is correct (uppercase UUID)

**"Status 2 showing as error"**
1. This is **correct behavior** for business errors
2. Status 2 = "Complete with Failures" (not system failure)
3. Insufficient funds is expected business outcome

### **Phase 3 Issues (Results)**

**"No execution summary"**
1. Ensure Phase 2 completed with terminal status
2. Check allocation endpoint accessibility
3. Verify Group ID is properly stored

---

## 🔧 Advanced Configuration

### **Timezone Handling**
```toml
# Server time is UTC+0
# South Africa time is UTC+2
# For immediate execution: triggerOnDate = null
# For scheduled: subtract 2 hours from local time
```

### **Testing Different Scenarios**

#### **Success Test**
- Use account with sufficient funds
- Expected: `groupStatusID: 1`

#### **Business Error Test**  
- Use account with insufficient funds
- Expected: `groupStatusID: 2` with "Complete with Failures"

#### **System Error Test**
- Disconnect VPN or use invalid token
- Expected: Connection or authentication errors

---

## 📚 Additional Resources

- **Complete API Documentation**: [API_INTEGRATION.md](API_INTEGRATION.md)
- **System Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Flow Verification**: [docs/API_Call_Flow_Verification.md](docs/API_Call_Flow_Verification.md)
- **Polling Implementation**: [docs/POLLING_EXPLANATION.md](docs/POLLING_EXPLANATION.md)
- **Postman Collection**: [postman/TradeAllocationsMonitor.postman_collection.json](postman/TradeAllocationsMonitor.postman_collection.json)

---

## ⚡ One-Line Setup

```bash
pip install -r requirements.txt && streamlit run app/main.py
```

**Remember**: Configure VPN + Bearer token for UAT environment access!

---

## 🎯 Current Implementation Status

- **✅ Phase 1**: Trade submission working perfectly
- **✅ Phase 2**: Polling and business error handling implemented  
- **✅ Phase 3**: Results retrieval and reporting functional
- **✅ UI**: Complete transparency and debugging tools
- **✅ Documentation**: Comprehensive guides and troubleshooting

**Ready for production use with proper API credentials!** 🚀