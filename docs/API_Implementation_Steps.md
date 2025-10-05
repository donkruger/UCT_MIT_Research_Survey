# Trade Allocations API - Implementation Steps

## Quick Start Implementation Guide

This document provides step-by-step instructions for integrating the Trade Allocations API into your existing Trading Sheet application.

## ✅ What's Already Been Created

The following components have been created and are ready for integration:

1. **API Client Module** (`app/api/trade_client.py`)
   - Complete Trade Allocations API client
   - Methods for order creation, status polling, and trade details retrieval
   - Error handling and retry logic

2. **Data Mapper Module** (`app/api/trade_mapper.py`)
   - CSV to API payload transformation
   - Validation and audit trail generation
   - Response formatting for display

3. **Status Component** (`app/components/trade_status.py`)
   - Real-time trade status monitoring UI
   - Visual progress indicators
   - Result summary displays

4. **Configuration Template** (`.streamlit/secrets.example.toml`)
   - Complete configuration structure
   - Environment-specific settings

## 📋 Implementation Steps

### Step 1: Configure API Credentials

1. Copy the secrets template:
```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

2. Update `.streamlit/secrets.toml` with your credentials:
```toml
[trade_api]
environment = "uat"  # Start with UAT for testing
system_identifier_id = 27
# Add API keys if required
```

### Step 2: Update the Submit Page

Modify `app/pages/3_Declaration_and_Submit.py` to integrate API submission:

```python
# Add imports at the top
from app.api.trade_client import TradeAllocationsClient
from app.api.trade_mapper import TradeDataMapper
from app.components.trade_status import render_trade_status, render_status_summary

# Add this function to handle API submission
def handle_trade_api_submission():
    """Execute trades via API and show status."""
    
    # Check for parsed data
    if 'trading_parser' not in st.session_state:
        st.error("No trading data found. Please upload a file first.")
        return False
    
    parser = st.session_state['trading_parser']
    
    # Prepare metadata
    metadata = {
        'user_name': st.session_state.get('consent_name', ''),
        'user_email': st.session_state.get('email', ''),
        'timestamp': datetime.now().isoformat(),
        'declaration_accepted': st.session_state.get('accept', False),
        'trader_id': st.session_state.get('trader_id', 45314)
    }
    
    # Initialize components
    mapper = TradeDataMapper()
    api_client = TradeAllocationsClient()
    
    # Validate data
    st.info("Validating trade data...")
    validation = mapper.validate_csv_data(parser.parsed_data)
    
    if not validation['valid']:
        st.error("Validation failed:")
        for error in validation['errors']:
            st.error(f"• {error}")
        return False
    
    if validation['warnings']:
        with st.expander("⚠️ Warnings"):
            for warning in validation['warnings']:
                st.warning(warning)
    
    # Map to API format
    with st.spinner("Preparing trade data..."):
        api_payload = mapper.map_csv_to_api(parser.parsed_data, metadata)
        st.session_state['api_payload'] = api_payload
    
    # Submit to API
    st.info(f"Submitting {len(api_payload['valueTradeAllocationRequestDTOS'])} trades...")
    submission_result = api_client.create_value_orders(api_payload)
    
    if submission_result['success']:
        st.success("✅ Trades submitted successfully!")
        
        # Monitor execution
        group_id = submission_result.get('groupId')
        st.session_state['trade_group_id'] = group_id
        
        # Show real-time status
        final_status = render_trade_status(group_id, api_client)
        
        # Format results
        api_results = mapper.format_api_response(final_status)
        st.session_state['api_results'] = api_results
        
        # Show summary
        render_status_summary(api_results)
        
        return True, api_results
    else:
        st.error(f"❌ Submission failed: {submission_result.get('message')}")
        return False, submission_result

# Replace the existing submit button logic with:
if st.button("Submit Trades", type="primary", use_container_width=True):
    if not st.session_state.get("accept"):
        st.error("Please accept the declaration first.")
    else:
        # Execute via API
        success, results = handle_trade_api_submission()
        
        if success:
            # Send enhanced email with API results
            from app.email_sender import send_trading_submission_email
            
            # Prepare enhanced payload with API results
            enhanced_payload = st.session_state['trading_parser'].prepare_api_payload(metadata)
            enhanced_payload['api_execution'] = results
            
            # Send email
            email_sent = send_trading_submission_email(
                recipient_email=st.session_state.get('email', ''),
                subject=f"Trade Execution Report - {results.get('group_id', 'N/A')[:8]}",
                body="Trade execution completed",
                payload_data=enhanced_payload
            )
            
            if email_sent:
                st.success("📧 Confirmation email sent")
            
            # Store for download
            st.session_state['submission_complete'] = True
```

### Step 3: Enhance Email Integration

Update `app/email_sender.py` to include API results in emails:

```python
def format_trade_execution_section(api_results: Dict[str, Any]) -> str:
    """Format trade execution results for email."""
    
    html = f"""
    <h3>Trade Execution Results</h3>
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Group ID:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{api_results.get('group_id', 'N/A')}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{api_results.get('status', 'PENDING')}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Environment:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{api_results.get('environment', 'UAT')}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Trades:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{api_results.get('trade_count', 0)}</td>
        </tr>
    </table>
    """
    
    if 'execution_summary' in api_results:
        summary = api_results['execution_summary']
        html += f"""
        <h4>Execution Summary</h4>
        <ul>
            <li>Successful: {summary.get('successful', 0)}</li>
            <li>Failed: {summary.get('failed', 0)}</li>
            <li>Pending: {summary.get('pending', 0)}</li>
        </ul>
        """
    
    return html

# Add to the email body in send_trading_submission_email:
if 'api_execution' in payload_data:
    body += format_trade_execution_section(payload_data['api_execution'])
```

### Step 4: Add Status Display to Main Page

Update `app/main.py` to show API connection status:

```python
# Add to the sidebar or main page
def show_api_status():
    """Display API connection status."""
    from app.api.trade_client import TradeAllocationsClient
    
    try:
        client = TradeAllocationsClient()
        
        # Test connection
        if client.test_connection():
            st.sidebar.success(f"✅ API Connected ({client.environment.upper()})")
        else:
            st.sidebar.warning("⚠️ API Connection Issue")
    except Exception as e:
        st.sidebar.error("❌ API Not Configured")
        
# Call in main page
show_api_status()
```

### Step 5: Test the Integration

1. **Test with sample data:**
```python
# Create test CSV
import pandas as pd

test_data = pd.DataFrame({
    'ShareCode': ['NGWINT', 'NGWINT'],
    'ContractCode': ['UT.ZA.NGWINT', 'UT.ZA.NGWINT'],
    'InstrumentID': [4257, 4257],
    'Units': [123.12345679, 123.12345679],
    'Amount': [1000.12, 1000.12],
    'Direction': ['BUY', 'SELL'],
    'UserID': [807686, 807686],
    'TrustAccount': [123456, 123456]
})

test_data.to_csv('test_trades.csv', index=False)
```

2. **Run the application:**
```bash
streamlit run app/main.py
```

3. **Test workflow:**
   - Complete the declaration
   - Upload test_trades.csv
   - Review the data
   - Submit and monitor status

## 🔧 Troubleshooting

### Common Issues and Solutions

1. **API Connection Failed**
   - Check network connectivity
   - Verify URLs in secrets.toml
   - Ensure firewall allows HTTPS to API domains

2. **Authentication Errors**
   - Verify API credentials if required
   - Check system_identifier_id = 27

3. **Timeout Issues**
   - Increase `api_timeout` in secrets.toml
   - Check if API is responding slowly

4. **Validation Errors**
   - Review CSV format matches expected structure
   - Check Direction values are 'BUY' or 'SELL'
   - Ensure all required columns are present

## 📊 Monitoring and Logs

### Add Logging

Create `app/utils/logger.py`:
```python
import logging
from datetime import datetime

def setup_logger():
    """Configure application logger."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'trade_api_{datetime.now():%Y%m%d}.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('TradeAPI')

# Use in API client
logger = setup_logger()
logger.info(f"Submitting {len(trades)} trades to {environment}")
```

### Track Metrics

Store execution metrics in session state:
```python
if 'api_metrics' not in st.session_state:
    st.session_state['api_metrics'] = {
        'total_submissions': 0,
        'successful_trades': 0,
        'failed_trades': 0,
        'average_time': 0
    }

# Update after each submission
st.session_state['api_metrics']['total_submissions'] += 1
```

## 📈 Next Steps

After successful implementation:

1. **Test in UAT thoroughly** with various trade scenarios
2. **Document test results** and any issues encountered
3. **Prepare for QA testing** once UAT is stable
4. **Plan production deployment** after QA approval
5. **Set up monitoring** for production environment
6. **Create user documentation** for the new feature

## 🆘 Support

For technical issues:
- Review the [API Integration Blueprint](API_Trade_Integration_Blueprint.md)
- Check the Postman collection for API examples
- Contact: api-support@easyequities.io

---

*Implementation Guide Version: 1.0*  
*Last Updated: December 2024*
