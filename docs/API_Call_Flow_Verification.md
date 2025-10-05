# API Call Flow Verification

## ✅ Sanity Check Complete

The implementation correctly follows the two-leg API flow:

## 🚀 **First Leg: Create Value Orders**

```
POST https://tradeallocationsapi.purple-uat.easyequities.io/tradeallocations/monitored/order/createValueOrdersWithSystemIdentifier
```

**Request Payload:**
```json
{
  "systemIdentifierID": 27,
  "groupId": "DDD86E90-E8BB-45F0-98DC-B4453D179782",  // Generated UUID
  "valueTradeAllocationRequestDTOS": [
    {
      "userID": 807686,
      "instrumentID": 4257,
      "trustAccountID": 123456,
      "amount": 1000.12,
      "units": 0,  // For value-based orders
      // ... other fields
    }
  ]
}
```

**Response:**
```json
{
  "groupID": "DDD86E90-E8BB-45F0-98DC-B4453D179782"
}
```

## 🔍 **Second Leg: Poll for Status**

Using the returned `groupID` from the first call:

```
GET https://trade-allocations-monitor.purple-uat.easyequities.io/tradeGroupStatus/DDD86E90-E8BB-45F0-98DC-B4453D179782
```

**Polling Loop:**
- Polls every 5 seconds
- Checks `overallStatus` field:
  - `0` = Incomplete (keep polling)
  - `1` = Group successful (stop - success)
  - `2` = Group complete with errors (stop - partial success)
- Maximum polling duration: 300 seconds (5 minutes)

## 🎯 **Implementation Verification**

### File: `app/api/trade_client.py`

✅ **Line 61:** Correct endpoint for creating value orders
```python
endpoint = f"{self.base_url}/tradeallocations/monitored/order/createValueOrdersWithSystemIdentifier"
```

✅ **Line 101:** Correctly extracts `groupID` from response
```python
group_id = result.get('groupID') or result.get('groupId')
```

✅ **Line 160:** Correct polling endpoint with group ID
```python
endpoint = f"{self.monitor_url}/tradeGroupStatus/{group_id}"
```

✅ **Lines 273-285:** Correctly checks `overallStatus` for completion
```python
if overall_status in [1, 2]:  # Terminal states
    # Get final allocation details
    allocations_result = self.get_all_trade_allocations(group_id)
```

### File: `app/pages/3_Declaration_and_Submit.py`

✅ **Line 339:** Calls first leg API
```python
submission_result = api_client.create_value_orders(api_payload)
```

✅ **Line 348:** Extracts returned group ID
```python
returned_group_id = submission_result.get('groupId', group_id)
```

✅ **Line 352:** Polls using extracted group ID
```python
final_status_result = api_client.poll_status(returned_group_id)
```

## 📊 **Enhanced UI Feedback**

The implementation now shows:
1. The exact URL being called for submission
2. The returned Group ID clearly displayed
3. The polling URL with full path
4. Real-time status updates during polling
5. Final status with allocation details

## ✨ **Conclusion**

The implementation correctly:
- ✅ Calls the value orders endpoint first
- ✅ Extracts the `groupID` from the response
- ✅ Uses that `groupID` for polling the status endpoint
- ✅ Handles asynchronous processing with proper polling
- ✅ Provides clear UI feedback at each step
