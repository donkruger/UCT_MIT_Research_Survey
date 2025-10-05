# Quick Setup Guide - Trade API Integration

## 🚀 Getting Started in 3 Steps

### Step 1: Configure API Settings

Your `.streamlit/secrets.toml` file has been created. You can use it as-is for testing, or customize it:

```toml
[trade_api]
environment = "uat"  # Use UAT for testing
system_identifier_id = 27
uat_base_url = "https://tradeallocationsapi.purple-uat.easyequities.io"
uat_monitor_url = "https://trade-allocations-monitor.purple-uat.easyequities.io"
api_timeout = 30
```

### Step 2: Test Your Setup

1. **Start the application:**
   ```bash
   streamlit run app/main.py
   ```

2. **Check API status:**
   - Look for the API status in the sidebar
   - Should show: "✅ API Connected (UAT)"

3. **Use the test button:**
   - Go to page 3 (Review & Execute)
   - Click "🧪 Test API Configuration"
   - Should show all green checkmarks

### Step 3: Execute Your First Trade

1. **Upload the sample CSV:**
   ```csv
   ShareCode,ContractCode,InstrumentID,Units,Amount,Direction,UserID,TrustAccount
   NGWINT,UT.ZA.NGWINT,4257,123.12345679,1000.12,BUY,807686,123456
   ```

2. **Follow the workflow:**
   - ✅ Accept declaration (page 1)
   - ✅ Upload CSV (main page)  
   - ✅ Review & execute (page 3)

## 🔧 Troubleshooting

### Issue: "API Not Configured" in Sidebar

**Solution:** Check that `.streamlit/secrets.toml` exists and has the `[trade_api]` section.

### Issue: "Connection Failed" When Testing

**Possible Causes:**
1. **Network issue** - Check internet connection
2. **Firewall** - Ensure HTTPS access to easyequities.io domains
3. **API unavailable** - Try again later

### Issue: Nothing Happens When Clicking Execute

**Now Fixed!** The new version provides immediate feedback:
- Shows "Button clicked! Starting execution..." instantly
- Displays step-by-step progress
- Shows detailed error messages if something fails

### Issue: API Submission Fails

**Check For:**
1. **Invalid data** - Verify CSV format is correct
2. **Authentication** - May need API keys for real submissions
3. **Permissions** - System ID 27 may need authorization

## 📧 Email Configuration

If you want to receive email confirmations:

```toml
[email_credentials]
email_address = "your-email@gmail.com"
app_password = "your-app-password"
```

## 🧪 Testing Workflow

### Test 1: Configuration Check
1. Click "🧪 Test API Configuration"
2. Should see all green checkmarks
3. If red errors, follow the specific instructions

### Test 2: Sample Trade Execution
1. Use the sample CSV data above
2. Complete declaration → upload → execute
3. Watch for step-by-step progress
4. Download execution reports

### Test 3: Error Handling
1. Try uploading invalid CSV (missing columns)
2. Verify error messages are clear
3. Test with network disconnected
4. Check that troubleshooting tips appear

## 📊 Expected API Flow

```
CSV Upload → Parse → Validate → Map to API → Submit → Monitor → Email → Complete
     ↓         ↓        ↓          ↓           ↓        ↓       ↓        ↓
  File Check  Data     Business   Swagger    Trade   Status  Audit   Reports
              Clean    Rules      Format     API     API     Trail   Available
```

## ✅ Success Indicators

When everything works correctly, you'll see:

1. **Sidebar**: "✅ API Connected (UAT)"
2. **Test Button**: All green checkmarks
3. **Execution**: Step-by-step progress with ✅ marks
4. **Final Result**: "🎉 Trades Submitted Successfully!"
5. **Email**: Confirmation with Group ID and execution details

## 🆘 Support

- **Documentation**: Check the `docs/` folder for detailed guides
- **Debug Tools**: Use the "🔧 Debug & Support" tab
- **Test Functions**: Use "Test API Configuration" button
- **Contact**: api-support@easyequities.io (include debug information)

---

## 🎯 Key Features Available

- ✅ **Real-time Feedback** - Immediate UI responses
- ✅ **Error Diagnostics** - Specific error messages with solutions
- ✅ **Test Tools** - Verify setup before executing
- ✅ **Download Reports** - JSON and CSV formats
- ✅ **Email Notifications** - With execution details
- ✅ **Session History** - Track all executions

Your Trade Allocations API integration is ready to use!

---

*Quick Setup Guide v1.0*  
*System Identifier: 27*
