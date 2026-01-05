#!/usr/bin/env python3
"""
Check if orphaned campaigns exist in the main 6 streak configs
"""

import requests
import json
import sys
from typing import Dict, List, Any, Tuple
from retool_integration import load_credentials


# The 6 main Heimdall configs to check
MAIN_CONFIGS = [
    "STREAK_ELIGIBILITY",
    "STREAK_TXN_ELIGIBILITY",
    "STREAK_CONFIG",
    "STREAK_BLOCK_TEMPLATE",
    "SCAN_HOMEPAGE_CONFIG",
    "PTP_STREAK_CONFIG"
]

# The 17 orphaned campaigns to search for
ORPHANED_CAMPAIGNS = {
    "axis_rupay_10_april": "df36a1e6-b8f8-4c57-a64e-6922d010d4c9",
    "snp_rup_may": "6d9fad25-66e9-4750-be8b-a5e9acdc5a24",
    "upi_cred_m0_zom": "91187d2d-c738-449d-8cd6-7bd960144248",
    "upi_na_zom": "4749c643-6b6a-42d1-a9c0-2d9379678284",
    "p2p_na_zom": "1519d77d-febc-40dc-bc18-5a25c885247d",
    "snp_na_zom": "4cc3621b-49c2-4922-9bb4-fa5543261ff6",
    "rupay_zomato": "8936f5a4-e594-4567-8fcb-1925b83e4587",
    "upi_50_feb": "72163f27-a0a3-4fca-b2c6-1c1e7aa47740",
    "upi_100_feb": "508f9e84-38a0-40da-af72-7a2443489df8",
    "snp_nonrupay_atc": "1e5cd37a-8aa1-4241-9c5d-fef4917ae303",
    "snp_nonrupay_m1_jun": "fbb8f2d4-2821-4c2d-afc8-73537b45fc09",
    "upi_activation_25x5_streak": "5b5e2346-61d1-4ef8-8a4e-9e9ca7203c18",
    "upi_act_20x5_streak": "9e6130ba-a5a3-4024-a519-dccdcf83ecd6",
    "upi_activation10x3_streak": "7849d4e6-79be-45e2-b7a4-9c1112424b00",
    "upi_activation_10x5_streak": "cd8da027-16f7-4c33-8711-2c9d77ee9645",
    "unknown_1": "35f2b8fd-0baf-48ef-97a1-26b9524312c3",
    "unknown_2": "316f7453-5236-4d43-a3d2-176fd8f5446c"
}


def fetch_config(config_key: str, userid: str, apikey: str) -> Tuple[bool, Any, str]:
    """Fetch a Heimdall config"""
    base_url = "http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template"
    url = f"{base_url}/{config_key}"
    headers = {
        'Content-Type': 'application/json',
        'userid': userid,
        '_cred_apikey': apikey
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return True, data, ""
    except Exception as e:
        return False, None, str(e)


def search_in_config(config_data: Any, campaign_name: str, campaign_uuid: str) -> List[str]:
    """
    Search for campaign name or UUID in config data
    Returns list of locations where found
    """
    locations = []
    config_str = json.dumps(config_data, indent=2).lower()

    # Search for campaign name
    if campaign_name.lower() in config_str:
        locations.append(f"name '{campaign_name}'")

    # Search for UUID
    if campaign_uuid.lower() in config_str:
        locations.append(f"UUID '{campaign_uuid}'")

    return locations


def main():
    print("\n" + "="*80)
    print("CHECKING ORPHANED CAMPAIGNS IN MAIN 6 STREAK CONFIGS")
    print("="*80)

    # Load credentials
    userid, apikey = load_credentials()
    if not userid or not apikey:
        print("❌ Error: Could not load credentials from credentials.json")
        sys.exit(1)

    print(f"\nSearching for {len(ORPHANED_CAMPAIGNS)} orphaned campaigns across {len(MAIN_CONFIGS)} configs...")

    # Track results
    results = {}

    # Check each config
    for config_key in MAIN_CONFIGS:
        print(f"\n📡 Fetching {config_key}...")
        success, config_data, error = fetch_config(config_key, userid, apikey)

        if not success:
            print(f"  ❌ Failed to fetch: {error}")
            continue

        print(f"  ✓ Fetched successfully")

        # Search for each orphaned campaign
        found_campaigns = []
        for campaign_name, campaign_uuid in ORPHANED_CAMPAIGNS.items():
            locations = search_in_config(config_data, campaign_name, campaign_uuid)
            if locations:
                found_campaigns.append({
                    'name': campaign_name,
                    'uuid': campaign_uuid,
                    'locations': locations
                })

        if found_campaigns:
            results[config_key] = found_campaigns
            print(f"  ⚠️  Found {len(found_campaigns)} orphaned campaigns in this config")
        else:
            print(f"  ✓ No orphaned campaigns found")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    if not results:
        print("\n✅ Good news! None of the 17 orphaned campaigns exist in the main 6 configs.")
        print("   They only exist in STREAK_JOURNEY_JOB_CONFIG and can be safely removed from there.")
    else:
        print(f"\n⚠️  Found orphaned campaigns in {len(results)} configs:\n")

        for config_key, campaigns in results.items():
            print(f"\n{config_key}:")
            for camp in campaigns:
                print(f"  • {camp['name']}")
                print(f"    UUID: {camp['uuid']}")
                print(f"    Found in: {', '.join(camp['locations'])}")

        print("\n" + "="*80)
        print("RECOMMENDATION")
        print("="*80)
        print("\nThese campaigns should be removed from ALL configs where they appear:")
        print("- STREAK_JOURNEY_JOB_CONFIG (supported_campaign_ids)")

        for config_key in results.keys():
            print(f"- {config_key}")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
