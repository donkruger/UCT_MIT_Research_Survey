# Trade Allocations API Integration Documentation

## Overview

This document describes the **complete and verified** API integration for the Trading Sheet Upload application with the EasyEquities Trade Allocations Monitor service. The application successfully processes Unit Trust (UT) trades through a **three-phase asynchronous execution pattern** using value-based orders.

## API Architecture

The integration follows a **proven three-phase asynchronous pattern**:

### 🚀 **Phase 1: Trade Submission**
- Submit trades to Trade Allocations API
- Receive Group ID for tracking
- Complete payload transparency

### 🔄 **Phase 2: Execution Monitoring**
- Poll Monitor service for execution status
- Handle business errors intelligently
- Real-time status updates

### 📊 **Phase 3: Results Retrieval**
- Fetch detailed execution results
- Generate comprehensive reports
- Send confirmation notifications

## API Endpoints

### 1. Submit Value Orders (Phase 1)

**Endpoint:** `POST /tradeallocations/monitored/order/createValueOrdersWithSystemIdentifier`

**Base URL:** `https://tradeallocationsapi.purple-uat.easyequities.io`

**Description:** Submit a batch of Unit Trust value-based trades for asynchronous processing.

**Headers:**
```http
Content-Type: application/json
Authorization: Bearer {api_token}
```

**Request Payload:**
```json
{
  "systemIdentifierID": 27,
  "groupId": "1AF0B1EE-543F-4726-AC2C-FD44D5AC5868",
  "valueTradeAllocationRequestDTOS": [
    {
      "userID": 807686,
      "instrumentID": 4257,
      "trustAccountID": 123456,
      "amount": 1000.12,
      "units": 0,
      "depositRequired": false,
      "costCalculationType": 1,
      "uniqueTransactionReference": "TSA_1AF0B1EE_0000",
      "dateCreated": "2025-09-29 18:00",
      "triggerOnDate": null,
      "trustAccountActionId": 7,
      "transactionTag": "NGWINT_BUY_0",
      "startAllocationProcessManually": false,
      "isCashMovement": false,
      "allowNegativeMovement": false,
      "traderID": 45314,
      "totalTradeRequestsInGroup": 1,
      "systemIdentifierID": 27
    }
  ]
}
```

**Key Payload Settings:**
- `triggerOnDate: null` - Immediate execution when markets open
- `startAllocationProcessManually: false` - Sets allocationStatusId to 0 (auto-execute)
- `units: 0` - Value-based trade (amount-driven, not unit-driven)

**Response (200 OK):**
```json
{
  "groupID": "1AF0B1EE-543F-4726-AC2C-FD44D5AC5868"
}
```

**Phase 1 Success Indicators:**
- HTTP 200 status code
- Valid Group ID returned (uppercase UUID format)
- Trade submission accepted for asynchronous processing

### 2. Monitor Trade Group Status (Phase 2)

**Endpoint:** `GET /tradeGroupStatus/{groupID}`

**Base URL:** `https://trade-allocations-monitor.purple-uat.easyequities.io`

**Description:** Poll for the execution status of a submitted trade group using the Group ID from Phase 1.

**Example URL:**
```
https://trade-allocations-monitor.purple-uat.easyequities.io/tradeGroupStatus/1AF0B1EE-543F-4726-AC2C-FD44D5AC5868
```

**Successful Completion Response:**
```json
{
  "groupID": "0E63A1B6-EDC0-4681-AB4B-1A47F8329435",
  "totalSuccess": 0,
  "totalFailed": 1,
  "totalTradesInGroup": 1,
  "groupStatusID": 2,
  "groupStatus": "Complete with Failures"
}
```

**Processing Response:**
```json
{
  "groupID": "1AF0B1EE-543F-4726-AC2C-FD44D5AC5868",
  "groupStatusID": 0,
  "groupStatus": "Processing"
}
```

**Status Field Values:**
- `groupStatusID: 0` = Incomplete (continue polling)
- `groupStatusID: 1` = Group successful (all trades executed)
- `groupStatusID: 2` = Complete with errors (business rule violations)

**Business Error Details:**
```
"Failed to process OrderAllocation: {"errorCode":400,"message":"Insufficient funds to place the order. Trade Costs will be: 2007.71. Free Cash = 1422.93"}"
```

### 3. Get Trade Allocation Details (Phase 3)

**Endpoint:** `GET /trade-monitor/allocation/all/{groupID}`

**Base URL:** `https://trade-allocations-monitor.purple-uat.easyequities.io`

**Description:** Retrieve detailed execution results for all trades in a group after completion.

**Response:**
```json
[
  {
    "allocationID": "12345",
    "userID": 807686,
    "instrumentID": 4257,
    "amount": 1000.12,
    "status": "FAILED",
    "executionTime": "2025-09-29T16:00:15.000Z",
    "message": "Insufficient funds",
    "errorDetails": "Trade Costs: 2007.71, Free Cash: 1422.93"
  }
]
```

## Implementation Status

### ✅ **Phase 1: Working**
- Trade submission successfully implemented
- Group ID generation and return confirmed
- Complete payload visibility and debugging
- Bearer token authentication working

### ✅ **Phase 2: Working** 
- Polling mechanism implemented and tested
- `groupStatusID` field detection working
- Business error handling implemented
- Real-time status updates working

### ✅ **Phase 3: Implemented**
- Results retrieval endpoint integrated
- Detailed execution summary display
- Business vs system error differentiation

## Processing Flow

### 1. Data Preparation
- User uploads CSV/Excel file with trade data
- System validates format and required columns
- Maps CSV fields to API payload format
- Generates unique Group ID (uppercase UUID)

### 2. Phase 1: Trade Submission
- Package trades into `valueTradeAllocationRequestDTOS` array
- Set `systemIdentifierID: 27` and unique `groupId`
- Submit to `/createValueOrdersWithSystemIdentifier`
- Receive and store Group ID from response
- Display submission success with Group ID

### 3. Phase 2: Execution Monitoring
- Start polling `/tradeGroupStatus/{groupID}` every 5 seconds
- Check `groupStatusID` for terminal states (1 or 2)
- Display real-time status: "Complete with Failures (ID: 2) | Success: 0 | Failed: 1"
- Handle business errors (insufficient funds) as expected outcomes
- Stop polling when terminal state reached

### 4. Phase 3: Results Processing
- Fetch detailed results from `/trade-monitor/allocation/all/{groupID}`
- Parse individual trade success/failure details
- Display execution summary with metrics
- Generate email confirmations with Group ID
- Archive results in execution history

## Error Handling

### Business Errors (Expected Outcomes)

#### **Insufficient Funds Example**
```json
{
  "groupStatusID": 2,
  "groupStatus": "Complete with Failures", 
  "totalSuccess": 0,
  "totalFailed": 1,
  "error": "Insufficient funds to place the order. Trade Costs: 2007.71. Free Cash: 1422.93"
}
```

**Application Response:**
- ⚠️ Shows "Execution Complete - Some Trades Failed"
- 📝 Explains this is normal for business rule violations
- 📊 Displays success/failure metrics
- ✅ Marks as successful API operation

### System Errors (Technical Issues)

#### **VPN/Connection Issues**
- **Symptom**: "Could not connect to the API server"
- **Solution**: Connect to VPN for UAT environment access

#### **Authentication Issues**
- **Symptom**: HTTP 401 responses
- **Solution**: Update Bearer token in secrets.toml

#### **Polling Issues**
- **Symptom**: Status remains at 0 for extended period
- **Solution**: Check backend processing, verify Group ID format

## Configuration

### Complete Environment Setup
```toml
[trade_api]
# Environment (requires VPN for UAT)
environment = "uat"
uat_base_url = "https://tradeallocationsapi.purple-uat.easyequities.io"
uat_monitor_url = "https://trade-allocations-monitor.purple-uat.easyequities.io"

# Authentication (required)
api_key = "your-bearer-token-here"

# System settings
system_identifier_id = 27
api_timeout = 30

# Polling configuration
status_polling_interval = 5
max_polling_duration = 300

# Trader settings
default_trader_id = 45314
```

## Testing

### Prerequisites
- VPN connection to UAT environment
- Valid Bearer token from EasyEquities API team
- Test account with known balance

### Test Scenarios

#### **Successful Trade**
1. Upload CSV with valid user having sufficient funds
2. Expected: `groupStatusID: 1` (success)
3. Result: All trades executed successfully

#### **Insufficient Funds Test**
1. Upload CSV with valid user having insufficient funds
2. Expected: `groupStatusID: 2` (complete with failures)
3. Result: Business error properly handled and displayed

#### **System Error Test**
1. Use invalid Bearer token or disconnect VPN
2. Expected: Connection or authentication errors
3. Result: Clear error messages and troubleshooting guidance

## Troubleshooting

### Phase 1 Issues
- **Connection Failed**: Check VPN connection
- **Authentication**: Verify Bearer token
- **Payload Errors**: Use payload preview to verify structure

### Phase 2 Issues  
- **No Polling**: Check for misplaced `st.stop()` statements
- **Status 0 Forever**: Backend processing delay or Group ID mismatch
- **Status 2 as Error**: Update logic to treat as business error, not system failure

### Phase 3 Issues
- **No Results**: Check allocation endpoint accessibility
- **Missing Details**: Verify Group ID format and backend data

## Support

For API issues or questions:
- **Technical Documentation**: [docs/API_Call_Flow_Verification.md](docs/API_Call_Flow_Verification.md)
- **Polling Details**: [docs/POLLING_EXPLANATION.md](docs/POLLING_EXPLANATION.md)
- **Postman Collection**: [postman/TradeAllocationsMonitor.postman_collection.json](postman/TradeAllocationsMonitor.postman_collection.json)
- **Email**: trading@easyequities.co.za

---

*Last Updated: September 2025*  
*Status: Phase 1 ✅ Working | Phase 2 ✅ Working | Phase 3 ✅ Implemented*