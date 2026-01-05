#!/bin/bash
# Startup script for Campaign Setup Web App
# Usage: ./start_web_app.sh

set -e

echo "========================================="
echo "Campaign Setup Web App Launcher"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then
    echo "Error: web_app.py not found!"
    echo "Please run this script from the campaign_setup directory"
    exit 1
fi

echo "✓ Found web_app.py"

# Kill any existing Streamlit processes
echo ""
echo "Checking for existing Streamlit processes..."
if pgrep -f "streamlit.*web_app" > /dev/null; then
    echo "Found existing Streamlit process. Killing..."
    pkill -9 -f "streamlit.*web_app" || true
    sleep 2
fi

# Check if port 8501 is in use
if lsof -ti:8501 > /dev/null 2>&1; then
    echo "Port 8501 is in use. Freeing it..."
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "✓ Port 8501 is free"

# Verify Python and dependencies
echo ""
echo "Checking dependencies..."
python3 -c "import streamlit" 2>/dev/null || {
    echo "Error: Streamlit not installed!"
    echo "Install with: pip3 install streamlit"
    exit 1
}
echo "✓ Streamlit is installed"

python3 -c "import requests" 2>/dev/null || {
    echo "Error: requests not installed!"
    echo "Install with: pip3 install requests"
    exit 1
}
echo "✓ requests is installed"

# Check required files
echo ""
echo "Checking required files..."
for file in credentials.json banner_registry.json subtitle_templates.json; do
    if [ ! -f "$file" ]; then
        echo "Warning: $file not found"
    else
        echo "✓ Found $file"
    fi
done

# Create backups directory if it doesn't exist
mkdir -p backups
echo "✓ Backups directory ready"

echo ""
echo "========================================="
echo "Starting Streamlit Web App..."
echo "========================================="
echo ""
echo "The app will open in your browser at:"
echo "  http://localhost:8501"
echo ""
echo "If the browser doesn't open automatically:"
echo "  1. Open your browser"
echo "  2. Go to: http://localhost:8501"
echo ""
echo "To stop the server: Press Ctrl+C"
echo ""
echo "========================================="
echo ""

# Start Streamlit
python3 -m streamlit run web_app.py \
    --server.port 8501 \
    --server.address localhost \
    --server.headless false \
    --browser.gatherUsageStats false
