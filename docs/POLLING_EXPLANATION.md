# Polling Implementation Explanation

## 📍 Location of Polling Code

The polling logic is implemented in:
**File:** `app/api/trade_client.py`
**Function:** `poll_status()` (lines 258-320)
**Helper Function:** `get_group_status()` (lines 157-195)

## 🔄 Polling Approach

### High-Level Flow
```
1. Submit trades → GET groupID
2. Start polling loop
3. GET /tradeGroupStatus/{groupID} every 5 seconds
4. Check overallStatus field:
   - 0 = Continue polling (incomplete)
   - 1 = Stop - Success
   - 2 = Stop - Completed with errors
5. If timeout (5 minutes), return last status
```

### Detailed Implementation

#### 1. Poll Status Function (`poll_status`)
```python
def poll_status(self, group_id: str, callback=None) -> Dict[str, Any]:
    max_duration = 300  # 5 minutes maximum
    interval = 5        # Poll every 5 seconds
    start_time = time.time()
    
    # Display polling info to user
    poll_url = f"{self.monitor_url}/tradeGroupStatus/{group_id}"
    st.info(f"🔍 Polling for status of Group ID: `{group_id}`")
    
    while time.time() - start_time < max_duration:
        # Call get_group_status
        status_result = self.get_group_status(group_id)
        
        # Check if we've reached a terminal state
        if status_result.get('success') and 'data' in status_result:
            overall_status = status_result['data'].get('overallStatus')
            
            if overall_status in [1, 2]:  # Terminal states
                # Get detailed results and return
                allocations_result = self.get_all_trade_allocations(group_id)
                status_result['allocations'] = allocations_result.get('allocations', [])
                return status_result
        
        # Wait 5 seconds before next poll
        time.sleep(interval)
    
    # Return timeout if max duration exceeded
    return {'success': False, 'status': 'TIMEOUT', ...}
```

#### 2. Get Group Status Function (`get_group_status`)
```python
def get_group_status(self, group_id: str) -> Dict[str, Any]:
    endpoint = f"{self.monitor_url}/tradeGroupStatus/{group_id}"
    
    try:
        response = self.session.get(endpoint, timeout=30)
        
        # Handle 404 as "PENDING" (expected in async system)
        if response.status_code == 404:
            return {
                'success': True,
                'status': 'PENDING',
                'data': {'overallStatus': 0},  # Incomplete
                'message': 'Trade group not yet registered. Status is PENDING.'
            }
        
        # Handle 200 success
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'status': data.get('status', 'UNKNOWN'),
                'data': data,
                'message': f'Status: {data.get("status", "UNKNOWN")}'
            }
        
        # Handle other status codes as errors
        else:
            return {
                'success': False,
                'status': 'ERROR',
                'message': f'HTTP {response.status_code}'
            }
    
    except Exception as e:
        return {
            'success': False,
            'status': 'ERROR', 
            'message': f'Request failed: {str(e)}'
        }
```

## 📊 Polling Configuration

### Default Settings
- **Polling Interval**: 5 seconds between requests
- **Maximum Duration**: 300 seconds (5 minutes)
- **Timeout per Request**: 30 seconds
- **Terminal States**: overallStatus 1 or 2

### Configurable via secrets.toml
```toml
[trade_api]
status_polling_interval = 5     # seconds between polls
max_polling_duration = 300      # maximum polling time
api_timeout = 30               # timeout per request
```

## 🎯 Key Status Values (from Trade Monitor docs)

According to the Trade Allocations Monitor documentation:

```
overallStatus Values:
- 0 = incomplete (keep polling)
- 1 = group successful (stop - all trades executed)
- 2 = group complete with errors (stop - some failed)
```

## 🔍 Troubleshooting the Polling

### Common Issues Your Colleague Should Check:

#### 1. **Initial 404 Response**
- **Expected Behavior**: First few polls may return 404
- **Why**: Trade group not yet registered in MongoDB
- **Our Handling**: Treat 404 as "PENDING" and continue polling

#### 2. **Incorrect URL Format**
- **Check**: Ensure Group ID is uppercase UUID format
- **Example**: `DDD86E90-E8BB-45F0-98DC-B4453D179782`
- **Full URL**: `https://trade-allocations-monitor.purple-uat.easyequities.io/tradeGroupStatus/{groupID}`

#### 3. **Asynchronous Delay**
- **Expected**: Trade processing takes time
- **Normal Range**: 30 seconds to 5 minutes
- **Backend Process**: Kafka → MongoDB → API response

#### 4. **Network/Authentication Issues**
- **Check**: Bearer token in requests
- **Verify**: Network connectivity to monitor URL
- **Test**: Manual curl request to same endpoint

## 🛠️ Debug Information Available

The code provides several debug points:

1. **Request Logging** (line 65-80):
   ```python
   st.session_state['last_api_request'] = {
       'endpoint': endpoint,
       'timestamp': datetime.now().isoformat(),
       'trade_count': len(payload.get('valueTradeAllocationRequestDTOS', [])),
       'environment': self.environment.upper()
   }
   ```

2. **Response Logging** (line 88-93):
   ```python
   st.session_state['last_api_response'] = {
       'status_code': response.status_code,
       'timestamp': datetime.now().isoformat(),
       'response_text': response.text[:500]
   }
   ```

3. **UI Debug Panel**: Available in the "Debug & Support" tab

## 🔧 Manual Testing Approach

To help diagnose the issue, your colleague can:

1. **Check Group ID Format**:
   ```bash
   # Should be uppercase UUID
   echo "DDD86E90-E8BB-45F0-98DC-B4453D179782" | grep -E '^[A-Z0-9-]{36}$'
   ```

2. **Test Manual Polling**:
   ```bash
   # Replace {groupID} with actual value
   curl -X GET \
     "https://trade-allocations-monitor.purple-uat.easyequities.io/tradeGroupStatus/DDD86E90-E8BB-45F0-98DC-B4453D179782" \
     -H "accept: application/json"
   ```

3. **Check MongoDB State** (Backend):
   - Verify trade group exists in MongoDB
   - Check Kafka message processing
   - Confirm overallStatus field updates

## 💡 Why Polling Might Fail

1. **Group ID Mismatch**: Generated ID doesn't match MongoDB record
2. **Backend Processing Delay**: Kafka/MongoDB not updating quickly
3. **Network Issues**: Connectivity to monitor service
4. **Authentication**: Bearer token issues
5. **API Service Issues**: Monitor service down/unavailable

The polling approach is standard for asynchronous systems - we continuously check until the backend signals completion via the `overallStatus` field.
