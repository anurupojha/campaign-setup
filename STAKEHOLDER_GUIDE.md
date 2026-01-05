# Campaign Setup Web App - Quick Start Guide for Stakeholders

## Getting Started

### Step 1: Start the Web App

Open Terminal and run:
```bash
cd ~/documents/campaign_setup
./start_web_app.sh
```

The web app will open automatically in your browser at: **http://localhost:8501**

---

## Using the Web App

### The 7-Step Wizard

The app guides you through 7 easy steps:

**Step 0: Login** 🔐
- Enter your API credentials
- Pre-filled if you've used it before
- Click "Login & Continue"

**Step 1: Basic Campaign Details** 📋
- Campaign name (e.g., `upi_streak_6`)
- Campaign ID (UUID from your team)
- Campaign type (UPI/SNP/P2P)
- Duration and max transactions

**Step 2: Transaction Details** 💰
- Minimum transaction amount
- Total campaign offer
- Per-transaction reward (auto-calculated)

**Step 3: Eligibility** ✅
- RuPay campaign? (yes/no)
- Bank-specific? (yes/no)
- If bank-specific: Enter issuer code

**Step 4: Banner Selection** 🎨
- Choose from existing banners
- Or upload a custom banner URL
- Custom banners are saved for future use

**Step 5: Subtitle Selection** 📝
- Choose from existing subtitles
- Or enter a custom subtitle
- Custom subtitles are saved for future use

**Step 6: Summary** 📊
- Review all your inputs
- See which configs will be processed
- Click "Process Campaign" to continue

**Step 7: Processing** ⚙️
- **Backup folder created here**
- Configs fetched from API
- Configs processed automatically
- Campaign summary generated
- Option to POST to production

---

## Where to Find Your Campaign Files

After Step 7 completes, find your campaign in:
```
~/documents/campaign_setup/backups/YYYY-MM-DD_campaign_name/
```

Example:
```
~/documents/campaign_setup/backups/2026-01-05_upi_streak_6/
```

**Each campaign folder contains:**
- `campaign_info.txt` - Full campaign summary
- `*_before.json` - Original configs (backup)
- `*_after.json` - Modified configs (ready to POST)
- `VERIFICATION_REPORT.txt` - Change verification

---

## Important Notes

### Custom Banners
- When you add a custom banner, it's saved to `banner_registry.json`
- It will appear in the dropdown on your next use
- ✓ This is normal and expected behavior

### Backup Folder
- **Only created in Step 7** after you click "Process Campaign"
- If you exit before Step 7, no backup is created
- ✓ This is intentional - only save completed campaigns

### Network Requirements
- Must be on corporate network or VPN
- API endpoint: `kongproxy.infra.dreamplug.net`
- If API calls fail, check your network connection

---

## Troubleshooting

### "Failed to Fetch" Error

**Quick Fix:**
1. Press `Cmd + Shift + R` (hard refresh)
2. Or try in incognito mode
3. Or restart: `./start_web_app.sh`

**See full troubleshooting guide:**
```bash
cat ~/documents/campaign_setup/WEB_APP_TROUBLESHOOTING.md
```

### Can't Start the App

```bash
# Kill any stuck processes
pkill -9 -f streamlit

# Start fresh
cd ~/documents/campaign_setup
./start_web_app.sh
```

### Need Help?

Run the diagnostic tool:
```bash
cd ~/documents/campaign_setup
python3 test_streamlit_app.py
```

This will check:
- ✓ Dependencies installed
- ✓ Data files present
- ✓ API connectivity
- ✓ Common issues

---

## Alternative: Terminal UI

If the web app has issues, use the terminal UI instead:
```bash
cd ~/documents/campaign_setup
python3 ui_enhanced.py
```

**Same functionality, no browser needed!**

---

## Stopping the Web App

In the terminal where the app is running:
- Press `Ctrl + C`

Or force kill:
```bash
pkill -9 -f streamlit
```

---

## Tips for Success

1. **Always complete all 7 steps** to ensure backup folder is created
2. **Review the summary** (Step 6) carefully before processing
3. **Check the backup folder** after Step 7 to verify files were created
4. **Use the verification report** to confirm changes before posting to production
5. **Test with a small campaign first** to familiarize yourself with the workflow

---

## Questions?

- **Technical issues:** See `WEB_APP_TROUBLESHOOTING.md`
- **Campaign setup questions:** See `SETUP_GUIDE_FOR_COLLEAGUES.md`
- **API/config questions:** See `SYSTEM_OVERVIEW.md`
