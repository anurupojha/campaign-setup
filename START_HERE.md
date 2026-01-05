# How to Use the Campaign Setup Wizard

## What Happened?

You got an error "folder doesn't exist" because **the app needs to run on your machine**, not on a cloud server.

**Why?** Our internal API (`kongproxy.infra.dreamplug.net`) uses private IP addresses and is only accessible from the company network.

---

## 🚀 Get Started (5 Minutes)

### Step 1: Clone the Repository

Open Terminal and paste this:

```bash
cd ~/Documents && git clone https://github.com/anurupojha/campaign-setup.git
```

Press Enter.

### Step 2: Install Requirements

```bash
cd campaign-setup && pip3 install -r requirements.txt
```

Press Enter. (Takes 1-2 minutes)

### Step 3: Start the App

```bash
./start_web_app.sh
```

Press Enter. The app will open in your browser automatically! 🎉

---

## 📱 Next Time You Use It

Just run:

```bash
cd ~/Documents/campaign-setup && ./start_web_app.sh
```

That's it!

---

## 🔄 Getting Updates

When new features are added:

```bash
cd ~/Documents/campaign-setup && git pull
```

---

## ❓ Troubleshooting

### "command not found: git"

Install Git:
```bash
xcode-select --install
```

### "command not found: pip3"

Install Python:
```bash
brew install python3
```

(Or download from https://python.org/)

### "port already in use"

Kill the old process:
```bash
pkill -9 -f streamlit
cd ~/Documents/campaign-setup && ./start_web_app.sh
```

### Need More Help?

Check these guides in the repo:
- `ONBOARDING_GUIDE.md` - Detailed setup
- `WEB_APP_TROUBLESHOOTING.md` - Common issues
- `STAKEHOLDER_GUIDE.md` - User guide

Or message the developer!

---

## ✨ What You Get

- **Browser-based interface** - No terminal commands needed
- **7-step wizard** - Guided workflow
- **Auto-backup** - All configs saved automatically
- **Visual selection** - Choose banners/subtitles from dropdown
- **Verification** - Review before posting to production

---

## 📋 Quick Reference

| Task | Command |
|------|---------|
| First time setup | `cd ~/Documents && git clone https://github.com/anurupojha/campaign-setup.git && cd campaign-setup && pip3 install -r requirements.txt` |
| Start the app | `cd ~/Documents/campaign-setup && ./start_web_app.sh` |
| Update to latest | `cd ~/Documents/campaign-setup && git pull` |
| Stop the app | Press `Ctrl + C` in terminal |

---

## 🎓 Alternative: Terminal UI

If you prefer terminal interface (no browser):

```bash
cd ~/Documents/campaign-setup && python3 ui_enhanced.py
```

Same functionality, just in the terminal!

---

## 🏢 For IT/DevOps: Internal Server Deployment

If you want **one server for everyone** (so they just open a URL), see:
- `STREAMLIT_CLOUD_DEPLOYMENT.md` (Option B: Internal Server Deployment)

---

## Summary

✅ Clone the repo (first time only)
✅ Run `./start_web_app.sh`
✅ App opens in browser
✅ Use the 7-step wizard

That's all! 🚀
