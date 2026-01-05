# Streamlit Cloud Deployment Guide

## The Right Way: Deploy Once, Share the Link

**Your stakeholders should NOT clone the repo or run anything locally.**

Instead:
1. **You deploy** the app to Streamlit Cloud (one time)
2. **You share** the public URL
3. **Stakeholders open** the link in their browser

That's it!

---

## How to Deploy to Streamlit Cloud

### Step 1: Go to Streamlit Cloud

Visit: https://share.streamlit.io/

Click **"Sign in with GitHub"**

### Step 2: Deploy New App

1. Click **"New app"**
2. Select repository: `anurupojha/campaign-setup`
3. Branch: `main`
4. Main file path: `web_app.py`
5. Click **"Deploy!"**

### Step 3: Get Your URL

Your app will be deployed at:
```
https://campaign-setup-[hash].streamlit.app
```
or
```
https://anurupojha-campaign-setup.streamlit.app
```

**This is the link you share with stakeholders!**

---

## Important: Environment Variables / Secrets

Your app needs API credentials. On Streamlit Cloud, you have two options:

### Option 1: Use Secrets Management (Recommended)

1. In your Streamlit Cloud dashboard, click on your app
2. Go to **Settings** → **Secrets**
3. Add your credentials:
   ```toml
   [credentials]
   userid = "96cc31b5-2f09-4b22-8f93-d6e46177a84d"
   apikey = "6d5ddcbedf09bd6a4a2651cd3bd8f1eca259e606979c0e2766c9548724dbe23e"
   ```
4. Update `web_app.py` to read from secrets:
   ```python
   # In step0_login(), check for secrets first:
   if "credentials" in st.secrets:
       saved_userid = st.secrets["credentials"]["userid"]
       saved_apikey = st.secrets["credentials"]["apikey"]
   ```

### Option 2: Let Users Enter Credentials (Current Approach)

The app already has a login screen (Step 0) where users enter credentials. This works but:
- ❌ Each stakeholder needs API credentials
- ❌ They have to enter them every time
- ✅ No secrets in code/repo

**Recommendation:** Use Option 1 (secrets) for easier stakeholder experience.

---

## After Deployment

### Share This with Stakeholders

"Hi team,

The Campaign Setup Wizard is now live at:
👉 https://your-app-url.streamlit.app

Just open the link in your browser - no installation needed!

Follow the 7-step wizard to set up campaigns. The app will:
- Guide you through all required inputs
- Create backup folders automatically
- Generate config files ready for review
- Optionally POST to production

Need help? Check the in-app sidebar or message me."

---

## Monitoring & Maintenance

### Check App Status
- Dashboard: https://share.streamlit.io/
- View logs: Click on your app → "Manage app" → "Logs"

### Update the App
Just push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Streamlit Cloud auto-detects changes and redeploys!

### Common Deployment Issues

#### Issue 1: App Crashes on Startup

**Check logs** in Streamlit Cloud dashboard.

Common causes:
- Missing dependencies in `requirements.txt`
- Import errors
- File path issues

**Current requirements.txt:**
```
streamlit>=1.28.0
rich>=13.0.0
requests>=2.31.0
```

#### Issue 2: "Failed to Fetch" in Deployed App

This can happen if:
- API endpoint is not accessible from Streamlit Cloud servers
- CORS issues
- Network/firewall blocking

**Solution:** Test API connectivity from external network:
```bash
curl -X GET "http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template/STREAK_CONFIG" \
  -H "userid: YOUR_USERID" \
  -H "_cred_apikey: YOUR_APIKEY"
```

If this fails from external network, the API is internal-only and **cannot be accessed from Streamlit Cloud**.

#### Issue 3: File System / Backups Not Working

Streamlit Cloud has ephemeral file systems. Files don't persist between sessions.

**Solutions:**
1. Use cloud storage (AWS S3, Google Cloud Storage)
2. Let users download files directly from the app
3. Email backup files to users

---

## File System Limitation (Important!)

⚠️ **Streamlit Cloud does NOT persist files between sessions.**

This means:
- `backups/` folder gets erased when app restarts
- Users can't access backup folders directly

**Fix Required:**

Update `step7_processing()` to:
1. Generate all files in memory
2. Create a ZIP file
3. Offer download button:
   ```python
   import zipfile
   from io import BytesIO

   # After processing...
   zip_buffer = BytesIO()
   with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
       for file in session_files:
           zip_file.write(file)

   st.download_button(
       label="📥 Download Campaign Files",
       data=zip_buffer.getvalue(),
       file_name=f"{campaign_name}_backup.zip",
       mime="application/zip"
   )
   ```

---

## Decision Tree

### Can the API be accessed from public internet?

**YES** → Deploy to Streamlit Cloud
- ✅ No setup for stakeholders
- ✅ Just share the URL
- ✅ Auto-updates from GitHub
- ⚠️ Need to add download button for backups

**NO** → Use internal deployment
- Deploy on internal server
- Or use the terminal UI (`ui_enhanced.py`)
- Stakeholders clone repo and run locally

---

## Testing Before Sharing

1. **Deploy to Streamlit Cloud**
2. **Test the public URL** yourself:
   - Go through all 7 steps
   - Verify API calls work
   - Check if backups can be accessed/downloaded
3. **If it works** → Share with stakeholders
4. **If API fails** → The API is internal-only, need different approach

---

## Alternative: If API is Internal-Only

If the API (`kongproxy.infra.dreamplug.net`) is not accessible from public internet:

### Option A: Deploy on Internal Server
- Set up Streamlit on company server
- Access via internal URL
- Same experience, just internal network only

### Option B: Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "web_app.py", "--server.port=8501"]
```

Deploy container on internal infrastructure.

### Option C: Keep Using Local Setup
Stakeholders run:
```bash
git clone https://github.com/anurupojha/campaign-setup.git
cd campaign-setup
pip3 install -r requirements.txt
streamlit run web_app.py
```

But this defeats the purpose of web deployment.

---

## Next Steps

1. **Test API accessibility** from external network
2. **Deploy to Streamlit Cloud** if API is public
3. **Add download button** for backup files
4. **Share URL** with stakeholders
5. **Monitor logs** for issues

---

## Quick Commands

```bash
# Push updates to trigger redeploy
git add .
git commit -m "Update"
git push origin main

# Check GitHub repo
open https://github.com/anurupojha/campaign-setup

# Access Streamlit Cloud dashboard
open https://share.streamlit.io/
```
