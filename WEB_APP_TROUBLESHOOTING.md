# Web App Troubleshooting Guide

## Quick Start (For Stakeholders)

### Option 1: Use the Startup Script (Recommended)
```bash
cd ~/documents/campaign_setup
./start_web_app.sh
```

The script will:
- ✓ Check all dependencies
- ✓ Kill any existing Streamlit processes
- ✓ Free up port 8501
- ✓ Start the web app
- ✓ Open your browser automatically

### Option 2: Manual Start
```bash
cd ~/documents/campaign_setup
python3 -m streamlit run web_app.py
```

Then open: http://localhost:8501

---

## Common Issues & Fixes

### Issue 1: "Failed to Fetch" Error in Browser

**Symptoms:**
- Web page loads but shows "Failed to fetch" or connection errors
- Blank page or loading spinner that never completes

**Solutions:**

1. **Hard Refresh the Browser**
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + Shift + R`
   - This clears the browser cache

2. **Try Incognito/Private Browsing Mode**
   - This bypasses cached data and extensions

3. **Clear Port and Restart**
   ```bash
   pkill -9 -f streamlit
   lsof -ti:8501 | xargs kill -9 2>/dev/null
   cd ~/documents/campaign_setup
   ./start_web_app.sh
   ```

4. **Check Browser Console for Errors**
   - Open DevTools: F12 or Cmd+Option+I
   - Go to Console tab
   - Look for red errors (WebSocket, CORS, or connection errors)

5. **Try a Different Browser**
   - Chrome, Firefox, or Safari
   - Different browsers handle WebSockets differently

### Issue 2: Port Already in Use

**Symptoms:**
```
Address already in use
```

**Solution:**
```bash
lsof -ti:8501 | xargs kill -9
# Or use a different port:
python3 -m streamlit run web_app.py --server.port 8502
```

### Issue 3: Streamlit Not Found

**Symptoms:**
```
command not found: streamlit
```

**Solution:**
```bash
pip3 install --upgrade streamlit
# Then use:
python3 -m streamlit run web_app.py
```

### Issue 4: Module Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Issue 5: Can't See Custom Banner After Upload

**Cause:** Custom banners are saved to `banner_registry.json` and will appear in the dropdown on next use.

**Solution:**
- The banner is saved successfully
- It will appear as an option the next time you run the app
- To verify: Check `banner_registry.json` for your new entry

### Issue 6: API Connection Errors

**Symptoms:**
- "Failed to fetch config"
- HTTP 401/403 errors

**Check:**
1. Verify credentials in `credentials.json`
2. Test API connection:
   ```bash
   python3 test_streamlit_app.py
   ```
3. Ensure you're on the corporate network/VPN

---

## Backup Folder Creation

**Important:** The backup folder is ONLY created in Step 7 (Processing Campaign).

Steps 1-6 collect information.
Step 7 creates the backup folder with format: `backups/YYYY-MM-DD_campaign_name/`

**To verify backup was created:**
```bash
ls -lt ~/documents/campaign_setup/backups/
```

The most recent folder should have today's date.

**Each backup contains:**
- `campaign_info.txt` - Campaign summary
- `*_before.json` - Original configs from API
- `*_after.json` - Modified configs ready to POST
- `VERIFICATION_REPORT.txt` - Verification summary

---

## Network/Firewall Issues

If the app loads but API calls fail:

1. **Check network connectivity:**
   ```bash
   curl -I http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template/STREAK_CONFIG
   ```

2. **Verify VPN connection** if required

3. **Check firewall settings** aren't blocking localhost

---

## For Developers

### Run Diagnostics
```bash
cd ~/documents/campaign_setup
python3 test_streamlit_app.py
```

This tests:
- ✓ Module imports
- ✓ Data files (banner_registry, subtitle_templates, credentials)
- ✓ API connectivity
- ✓ Banner image URLs
- ✓ Streamlit version compatibility

### View Streamlit Logs
```bash
tail -f ~/.streamlit/logs/streamlit.log
```

### Debug Mode
Add this to the top of web_app.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Configuration File

Location: `~/.streamlit/config.toml`

Current settings:
```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "localhost"
```

---

## Still Having Issues?

1. **Run the diagnostic script:**
   ```bash
   python3 test_streamlit_app.py
   ```

2. **Use the terminal UI instead:**
   ```bash
   python3 ui_enhanced.py
   ```
   (Works without browser, same functionality)

3. **Check this troubleshooting guide for your specific error message**

4. **Collect information and report:**
   - Error message from browser console
   - Output of `python3 test_streamlit_app.py`
   - Streamlit version: `python3 -m streamlit version`
   - OS and browser version
