# Stakeholder Onboarding Guide

## Quick Answer: How Do I Use This?

Your stakeholder needs to run the app **on their machine** (connected to company network/VPN).

**Why?** The API (`kongproxy.infra.dreamplug.net`) uses private IP addresses and is only accessible from the internal company network.

---

## One-Time Setup (For Each Stakeholder)

### Step 1: Clone the Repository

```bash
cd ~/Documents
git clone https://github.com/anurupojha/campaign-setup.git
cd campaign-setup
```

### Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

That's it! Setup complete.

---

## Daily Usage

### Start the Web App

```bash
cd ~/Documents/campaign-setup
./start_web_app.sh
```

The app will open in your browser at: http://localhost:8501

### Or Use Terminal UI (No Browser)

```bash
cd ~/Documents/campaign-setup
python3 ui_enhanced.py
```

---

## For Non-Technical Stakeholders

Send them this:

```
Hi [Name],

To use the Campaign Setup Wizard:

1. Open Terminal
2. Copy-paste this command and press Enter:

cd ~/Documents && git clone https://github.com/anurupojha/campaign-setup.git && cd campaign-setup && pip3 install -r requirements.txt

3. When that finishes, run:

./start_web_app.sh

4. The app will open in your browser automatically

5. Next time, just run:
cd ~/Documents/campaign-setup && ./start_web_app.sh

Let me know if you hit any issues!
```

---

## Troubleshooting for Stakeholders

### "folder doesn't exist"

They need to clone the repo first:
```bash
cd ~/Documents
git clone https://github.com/anurupojha/campaign-setup.git
```

### "command not found: git"

Install Git:
- Mac: `xcode-select --install`
- Windows: Download from https://git-scm.com/

### "command not found: pip3"

Install Python:
- Mac: `brew install python3`
- Windows: Download from https://python.org/

### "port already in use"

Kill existing process:
```bash
pkill -9 -f streamlit
./start_web_app.sh
```

### "failed to fetch" or API errors

Check they're on company network/VPN:
```bash
ping kongproxy.infra.dreamplug.net
```

Should show responses. If "cannot resolve" → not on VPN.

---

## Updating to Latest Version

When you push updates:

```bash
cd ~/Documents/campaign-setup
git pull origin main
./start_web_app.sh
```

---

## Alternative: Deploy on Internal Server

If you have an internal server accessible to all stakeholders:

### Option A: Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t campaign-setup .
docker run -p 8501:8501 campaign-setup
```

Access at: `http://internal-server:8501`

### Option B: Direct Server Deployment

```bash
# On the server
git clone https://github.com/anurupojha/campaign-setup.git
cd campaign-setup
pip3 install -r requirements.txt

# Run as service
nohup streamlit run web_app.py --server.port=8501 --server.address=0.0.0.0 &
```

Stakeholders access: `http://internal-server.company.com:8501`

---

## Why Not Streamlit Cloud?

**TL;DR:** The API is internal-only (private IP: 172.23.x.x), so Streamlit Cloud (public internet) can't reach it.

**Options:**
1. ✅ **Current approach** - Each user runs locally
2. ✅ **Internal server** - One server, all users access via URL
3. ❌ **Streamlit Cloud** - Won't work (can't reach internal API)

---

## Comparison

| Approach | Setup Effort | User Experience | Best For |
|----------|--------------|-----------------|----------|
| Local (current) | Medium (clone + install) | Good (browser UI) | Small teams |
| Internal Server | High (deploy once) | Best (just open URL) | Large teams |
| Terminal UI | Low (clone + install) | OK (terminal only) | Power users |

---

## Making It Easier

### Create Installation Script

Save as `install.sh`:
```bash
#!/bin/bash
cd ~/Documents
git clone https://github.com/anurupojha/campaign-setup.git
cd campaign-setup
pip3 install -r requirements.txt
echo "Setup complete! Run: cd ~/Documents/campaign-setup && ./start_web_app.sh"
```

Share one command:
```bash
curl -s https://raw.githubusercontent.com/anurupojha/campaign-setup/main/install.sh | bash
```

### Create Desktop Shortcut (Mac)

Save as `Campaign Setup.app`:
```bash
#!/bin/bash
cd ~/Documents/campaign-setup
./start_web_app.sh
```

---

## Summary for Your Situation

**What stakeholders need to do:**

1. **First time only:**
   ```bash
   cd ~/Documents
   git clone https://github.com/anurupojha/campaign-setup.git
   cd campaign-setup
   pip3 install -r requirements.txt
   ```

2. **Every time they use it:**
   ```bash
   cd ~/Documents/campaign-setup
   ./start_web_app.sh
   ```

3. **To update:**
   ```bash
   cd ~/Documents/campaign-setup
   git pull
   ```

**The "folder doesn't exist" error** = They skipped step 1 (cloning the repo).

---

## Quick Onboarding Email Template

```
Subject: Campaign Setup Wizard - Get Started

Hi team,

Here's how to set up the Campaign Setup Wizard on your machine:

📥 **One-Time Setup (5 minutes):**

1. Open Terminal
2. Run these commands:

cd ~/Documents
git clone https://github.com/anurupojha/campaign-setup.git
cd campaign-setup
pip3 install -r requirements.txt

🚀 **Daily Usage:**

cd ~/Documents/campaign-setup
./start_web_app.sh

The web app will open automatically in your browser!

🔄 **To Get Updates:**

cd ~/Documents/campaign-setup
git pull

📚 **Need Help?**
Check: ~/Documents/campaign-setup/STAKEHOLDER_GUIDE.md

Or message me!
```

---

## Next Steps

1. Test the `./start_web_app.sh` script yourself
2. Share the onboarding email with one stakeholder first
3. Help them through setup over screen share if needed
4. Once working, share with rest of team
5. Consider internal server deployment if team is large
