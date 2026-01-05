# Campaign Setup Web App - Quick Start Guide

## 🚀 Run Your Web Demo

### Step 1: Install Dependencies
```bash
cd ~/documents/campaign_setup
pip3 install -r requirements.txt
```

### Step 2: Launch the Web App
```bash
streamlit run web_app.py
```

### Step 3: Access in Browser
The app will automatically open in your browser at:
```
http://localhost:8501
```

If it doesn't open automatically, just copy that URL into your browser.

## 🎯 Features

Your web demo includes:
- ✅ Multi-step wizard interface
- ✅ Progress tracking in sidebar
- ✅ Real-time form validation
- ✅ Banner preview
- ✅ Beautiful UI with responsive design
- ✅ All functionality from the terminal version

## 🛑 Stop the Server

Press `Ctrl + C` in the terminal where the app is running.

## 📝 Notes

- The web app uses the same backend logic as your terminal version
- All data is stored in the same session folders
- You can run both versions (terminal and web) as needed
- Default port is 8501, but Streamlit will use another port if it's busy

## 🔧 Troubleshooting

**Port already in use?**
```bash
streamlit run web_app.py --server.port 8502
```

**Need to share with others on your network?**
```bash
streamlit run web_app.py --server.address 0.0.0.0
```

Then access via: `http://YOUR_IP:8501`

## 🎨 Customize

To change the theme, create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#00d4ff"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f8ff"
textColor = "#262730"
```

Enjoy your demo! 🎉
