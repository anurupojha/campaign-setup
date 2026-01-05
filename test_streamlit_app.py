#!/usr/bin/env python3
"""
Diagnostic script to test Streamlit app components
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("STREAMLIT APP DIAGNOSTICS")
print("=" * 70)

# Test 1: Import check
print("\n[Test 1] Testing imports...")
try:
    import streamlit as st
    print("✓ Streamlit imported successfully")
    print(f"  Version: {st.__version__}")
except Exception as e:
    print(f"✗ Streamlit import failed: {e}")
    sys.exit(1)

try:
    from setup_campaign_master import (
        load_credentials, load_banner_registry, load_subtitle_templates,
        determine_configs_needed, create_session_folder,
        fetch_config, process_config, generate_campaign_info,
        post_all_configs
    )
    print("✓ setup_campaign_master imported successfully")
except Exception as e:
    print(f"✗ setup_campaign_master import failed: {e}")
    sys.exit(1)

try:
    from retool_integration import (
        HeimdalJourneyConfigAPI, parse_value_field,
        add_campaign_to_config, check_campaign_exists
    )
    print("✓ retool_integration imported successfully")
except Exception as e:
    print(f"✗ retool_integration import failed: {e}")
    sys.exit(1)

# Test 2: Data files check
print("\n[Test 2] Testing data files...")
try:
    banner_registry = load_banner_registry()
    print(f"✓ banner_registry.json loaded ({len(banner_registry['banners'])} banners)")
except Exception as e:
    print(f"✗ Failed to load banner_registry.json: {e}")

try:
    subtitle_data = load_subtitle_templates()
    print(f"✓ subtitle_templates.json loaded ({len(subtitle_data['subtitles'])} subtitles)")
except Exception as e:
    print(f"✗ Failed to load subtitle_templates.json: {e}")

try:
    credentials = load_credentials()
    if credentials:
        print(f"✓ credentials.json loaded (userid: {credentials.get('userid', 'N/A')[:20]}...)")
    else:
        print("⚠ credentials.json is empty or missing")
except Exception as e:
    print(f"✗ Failed to load credentials.json: {e}")

# Test 3: API connectivity
print("\n[Test 3] Testing API connectivity...")
try:
    credentials = load_credentials()
    if credentials:
        api = HeimdalJourneyConfigAPI(credentials['userid'], credentials['apikey'])
        print("✓ API client initialized")

        print("  Testing API connection...")
        success, config_data, error = api.get_config()
        if success:
            print(f"✓ API connection successful")
            print(f"  Config key: {config_data.get('key', 'N/A')}")
        else:
            print(f"✗ API connection failed: {error}")
    else:
        print("⚠ Skipping API test (no credentials)")
except Exception as e:
    print(f"✗ API test failed: {e}")

# Test 4: Image URL accessibility
print("\n[Test 4] Testing banner image URLs...")
try:
    import requests
    banner_registry = load_banner_registry()
    test_url = banner_registry['banners'][0]['url']
    print(f"  Testing: {test_url}")

    response = requests.head(test_url, timeout=5)
    if response.status_code == 200:
        print(f"✓ Banner images are accessible (Status: {response.status_code})")
    else:
        print(f"⚠ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"✗ Image URL test failed: {e}")

# Test 5: Check Streamlit version compatibility
print("\n[Test 5] Checking Streamlit compatibility...")
try:
    import streamlit as st
    version = st.__version__
    major, minor = map(int, version.split('.')[:2])

    if major > 1 or (major == 1 and minor >= 13):
        print(f"✓ Streamlit version {version} should support use_container_width")
    else:
        print(f"⚠ Streamlit version {version} might not support use_container_width")
        print("  Consider upgrading: pip install --upgrade streamlit")
except Exception as e:
    print(f"✗ Version check failed: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)

print("\nNext steps:")
print("1. If all tests pass, try: python3 -m streamlit run web_app.py")
print("2. Check browser console for JavaScript errors")
print("3. Look for CORS or network errors in browser DevTools")
