#!/usr/bin/env python3
"""
Remove 4 cred_mtu campaigns from other streak templates (except STREAK_BLOCK_TEMPLATE)
"""

import requests
import json
import sys
from typing import Dict, Any, List, Tuple
from retool_integration import load_credentials

# Base URL
BASE_URL = "http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template"

# Campaigns to remove
CAMPAIGNS_TO_REMOVE = [
    "cred_mtu_multi_lob_at_risk_retention",
    "cred_mtu_multi_lob_freq_snp_churn_retention",
    "cred_mtu_multi_lob_others_retention",
    "cred_mtu_single_lob_freq_snp_churn_retention"
]

# Configs to clean (EXCLUDING STREAK_BLOCK_TEMPLATE per user requirement)
CONFIGS_TO_CLEAN = [
    "STREAK_ELIGIBILITY",
    "STREAK_TXN_ELIGIBILITY",
    "STREAK_CONFIG",
    "SCAN_HOMEPAGE_CONFIG",
    "PTP_STREAK_CONFIG"
]


def fetch_config(config_key: str, headers: Dict[str, str]) -> Tuple[bool, Dict[str, Any], str]:
    """Fetch a config"""
    try:
        url = f"{BASE_URL}/{config_key}"
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            return True, response.json(), ""
        else:
            return False, {}, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, {}, str(e)


def clean_config_value(value_str: str, campaigns: List[str]) -> Tuple[str, int]:
    """Remove campaign references from value string"""
    removed_count = 0

    try:
        value_obj = json.loads(value_str)

        def clean_obj(obj):
            nonlocal removed_count
            if isinstance(obj, dict):
                for key, val in list(obj.items()):
                    if key in campaigns:
                        del obj[key]
                        removed_count += 1
                    else:
                        obj[key] = clean_obj(val)
            elif isinstance(obj, list):
                new_list = []
                for item in obj:
                    if isinstance(item, str) and item in campaigns:
                        removed_count += 1
                    else:
                        new_list.append(clean_obj(item) if not isinstance(item, str) else item)
                obj[:] = new_list
            return obj

        cleaned = clean_obj(value_obj)
        return json.dumps(cleaned, indent=2), removed_count

    except json.JSONDecodeError:
        # If it's not JSON (like STREAK_BLOCK_TEMPLATE), return as-is
        return value_str, 0


def update_config(config_data: Dict[str, Any], headers: Dict[str, str]) -> Tuple[bool, str]:
    """Update a config"""
    try:
        response = requests.post(BASE_URL, json=config_data, headers=headers, timeout=30)

        if response.status_code == 200:
            return True, "Success"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)


def main():
    print("\n" + "="*80)
    print("CLEANUP 4 CRED_MTU CAMPAIGNS FROM STREAK TEMPLATES")
    print("="*80)

    print(f"\nCampaigns to remove ({len(CAMPAIGNS_TO_REMOVE)}):")
    for i, campaign in enumerate(CAMPAIGNS_TO_REMOVE, 1):
        print(f"  {i}. {campaign}")

    print(f"\nConfigs to clean ({len(CONFIGS_TO_CLEAN)}):")
    for i, config in enumerate(CONFIGS_TO_CLEAN, 1):
        print(f"  {i}. {config}")

    print("\n(STREAK_BLOCK_TEMPLATE excluded to preserve image URLs)")

    # Load credentials
    userid, apikey = load_credentials()
    if not userid or not apikey:
        print("❌ Error: Could not load credentials")
        sys.exit(1)

    headers = {
        'Content-Type': 'application/json',
        'userid': userid,
        '_cred_apikey': apikey
    }

    total_removed = 0
    results = []

    # Process each config
    for config_key in CONFIGS_TO_CLEAN:
        print(f"\n{'='*80}")
        print(f"Processing: {config_key}")
        print('='*80)

        # Fetch
        print("  📡 Fetching...")
        success, config_data, error = fetch_config(config_key, headers)
        if not success:
            print(f"  ❌ Failed to fetch: {error}")
            results.append((config_key, 0, False, error))
            continue

        # Clean
        print("  🔍 Cleaning...")
        original_value = config_data.get('value', '')
        cleaned_value, removed = clean_config_value(original_value, CAMPAIGNS_TO_REMOVE)

        if removed == 0:
            print(f"  ✓ No references found (already clean)")
            results.append((config_key, 0, True, "Already clean"))
            continue

        print(f"  🗑️  Found {removed} reference(s) to remove")

        # Update
        config_data['value'] = cleaned_value
        config_data['updated_by'] = "campaign_cleanup_cred_mtu_templates"

        print("  📤 Updating...")
        success, message = update_config(config_data, headers)

        if success:
            print(f"  ✅ Success! Removed {removed} reference(s)")
            total_removed += removed
            results.append((config_key, removed, True, "Success"))
        else:
            print(f"  ❌ Failed to update: {message}")
            results.append((config_key, removed, False, message))

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    for config_key, removed, success, message in results:
        status = "✅" if success else "❌"
        print(f"{status} {config_key}: {removed} removed - {message}")

    print(f"\nTotal references removed: {total_removed}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
