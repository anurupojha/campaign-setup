# Setup Guide for Colleagues

## Campaign Setup Web Interface - User Guide

This guide helps colleagues access and use the Campaign Setup web interface without needing Claude Code.

---

## Prerequisites

1. **Python 3.8 or higher** installed on their machine
2. **Terminal/Command Line** access
3. **Network access** to production APIs

---

## One-Time Setup

### Step 1: Get the Campaign Setup Folder

Copy the entire `campaign_setup` folder to your colleague's machine:

```bash
# From your machine, create a zip
cd ~/documents
zip -r campaign_setup.zip campaign_setup/

# Send campaign_setup.zip to your colleague
# They should extract it to their documents folder
```

**Or use Git** (if you have a repository):
```bash
git clone <repository-url> ~/documents/campaign_setup
```

### Step 2: Install Required Python Packages

Your colleague needs to install these packages:

```bash
pip3 install streamlit requests rich
```

**Or create a requirements.txt:**
```bash
cd ~/documents/campaign_setup
pip3 install -r requirements.txt
```

### Step 3: Setup Credentials

Your colleague needs API credentials. Create `credentials.json`:

```bash
cd ~/documents/campaign_setup
```

Create file: `credentials.json`
```json
{
  "userid": "their_user_id",
  "apikey": "their_api_key"
}
```

**Important:** This file should NEVER be committed to git (already in .gitignore)

---

## Running the Web Interface

### Start the Web App

```bash
cd ~/documents/campaign_setup
streamlit run web_app.py
```

This will:
1. Start a local web server
2. Automatically open your browser to `http://localhost:8501`
3. If browser doesn't open, manually go to: `http://localhost:8501`

### Stopping the Web App

Press `Ctrl+C` in the terminal where it's running

---

## Using the Web Interface

### Workflow Steps:

1. **Basic Campaign Details**
   - Campaign Name
   - Campaign ID (UUID from team)
   - Campaign Type (UPI/SNP/P2P)
   - Duration and max transactions

2. **Transaction Details**
   - Min transaction amount
   - Total campaign offer
   - Auto-calculates per-transaction reward

3. **Additional Eligibility**
   - RuPay campaign (yes/no)
   - Bank-specific (yes/no)

4. **Banner Selection**
   - Choose from existing banners
   - Or add custom banner URL

5. **Bottom Sheet Subtitle**
   - Choose from templates
   - Or enter custom text

6. **Review Summary**
   - Check all details
   - See which configs will be updated

7. **Process Campaign**
   - Generates config files locally
   - Review before posting
   - **POST to Production** button (with confirmation)
   - **Update Retool Config** automatically
     - Checkbox: "Is this a chain campaign?"
     - If yes: Enter next campaign name
     - Validates campaign exists
     - Updates STREAK_JOURNEY_JOB_CONFIG

---

## Features

### ✅ Safety Features
- Files generated locally first (can review before posting)
- Explicit "POST to Production" button
- Duplicate detection (won't add campaigns twice)
- Chain validation (verifies next campaign exists)

### ✅ User-Friendly
- Web interface (no terminal commands needed)
- Progress indicators
- Clear error messages
- Step-by-step wizard
- Back/Next navigation

### ✅ Complete Workflow
- Generates all streak configs
- Updates Retool dashboard automatically
- Creates session folders with all files
- Generates campaign_info.txt summary

---

## Sharing the Web Interface

### Option 1: Each User Runs Locally (Recommended)
- Each colleague follows setup steps above
- Runs `streamlit run web_app.py` on their machine
- Access at `http://localhost:8501`

**Pros:**
- Simple setup
- No server maintenance
- Each user has their own session
- No security concerns

**Cons:**
- Each user needs Python installed
- Each user needs credentials file

### Option 2: Deploy to Shared Server (Advanced)

If you want ONE instance everyone accesses:

#### Using Streamlit Cloud (Free):
1. Create GitHub repository with campaign_setup folder
2. Go to https://streamlit.io/cloud
3. Connect GitHub repo
4. Deploy web_app.py
5. Share the URL (e.g., https://your-app.streamlit.app)

**Security Note:** Credentials should NOT be in the repo. Use Streamlit secrets instead.

#### Using Internal Server:
```bash
# On server
streamlit run web_app.py --server.port 8501 --server.address 0.0.0.0
```

Then access via: `http://server-ip:8501`

---

## File Structure

```
~/documents/campaign_setup/
├── web_app.py                      # Web interface (main file)
├── ui_enhanced.py                  # Terminal version (alternative)
├── setup_campaign_master.py        # Core logic
├── retool_integration.py           # Retool API integration
├── credentials.json                # API credentials (each user needs this)
├── banner_registry.json            # Banner templates
├── subtitle_templates.json         # Subtitle templates
├── test_retool_integration.py      # Test script (optional)
└── sessions/                       # Generated campaign files
    └── campaign_name_YYYYMMDD_HHMMSS/
        ├── campaign_info.txt
        ├── STREAK_CONFIG_original.json
        ├── STREAK_CONFIG_modified.json
        └── ...
```

---

## Troubleshooting

### "Command not found: streamlit"
**Solution:** Install streamlit: `pip3 install streamlit`

### "Module not found: requests" or "Module not found: rich"
**Solution:** Install missing packages: `pip3 install requests rich`

### "No saved credentials found"
**Solution:** Create `credentials.json` with userid and apikey

### "Port 8501 already in use"
**Solution:**
- Stop existing streamlit process: `pkill -f streamlit`
- Or use different port: `streamlit run web_app.py --server.port 8502`

### Browser doesn't open automatically
**Solution:** Manually open: `http://localhost:8501`

### "Failed to fetch config"
**Solution:** Check:
- Credentials are correct in credentials.json
- Network access to production APIs
- VPN connected (if required)

---

## Quick Reference

### Start Web App
```bash
cd ~/documents/campaign_setup
streamlit run web_app.py
```

### Stop Web App
Press `Ctrl+C` in terminal

### Test Without Production Changes
```bash
python3 test_retool_integration.py
```

### Terminal Version (Alternative)
```bash
python3 ui_enhanced.py
```

---

## Security Best Practices

1. **Never commit credentials.json** to git
2. **Keep API keys secure** (don't share in chat/email)
3. **Review configs** before clicking "POST to Production"
4. **Use separate credentials** for each user (don't share)
5. **Check campaign details** carefully in summary step

---

## Support

If your colleague encounters issues:

1. Check this guide's troubleshooting section
2. Verify Python version: `python3 --version` (should be 3.8+)
3. Verify packages installed: `pip3 list | grep -E "streamlit|requests|rich"`
4. Check credentials.json exists and has correct format
5. Try test script first: `python3 test_retool_integration.py`

---

## Updates

To update to latest version:

```bash
cd ~/documents/campaign_setup
# If using git:
git pull

# If using zip:
# Get new zip file and extract, replacing old files
```

---

**Last Updated:** 2026-01-03
**Version:** 2.0 (with Retool integration)
