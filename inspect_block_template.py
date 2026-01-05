#!/usr/bin/env python3
"""
Inspect STREAK_BLOCK_TEMPLATE to understand structure before cleanup
"""

import requests
import json
import sys
from retool_integration import load_credentials


def fetch_config(config_key: str, userid: str, apikey: str):
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
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def main():
    print("\n" + "="*80)
    print("INSPECTING STREAK_BLOCK_TEMPLATE STRUCTURE")
    print("="*80)

    # Load credentials
    userid, apikey = load_credentials()
    if not userid or not apikey:
        print("❌ Error: Could not load credentials")
        sys.exit(1)

    # Fetch config
    print("\n📡 Fetching STREAK_BLOCK_TEMPLATE...")
    config_data = fetch_config("STREAK_BLOCK_TEMPLATE", userid, apikey)
    print("✓ Fetched successfully\n")

    # Save raw config first for inspection
    with open('streak_block_template_raw.json', 'w') as f:
        json.dump(config_data, f, indent=2)

    print(f"📋 Top-level keys in config: {list(config_data.keys())}\n")

    # Parse value field if it exists
    if 'value' in config_data:
        print(f"✓ Found 'value' field, attempting to parse...")
        print(f"  Value type: {type(config_data['value'])}")
        print(f"  Value length: {len(str(config_data['value']))} chars\n")

        try:
            value_obj = json.loads(config_data['value'])

            # Save to file for inspection
            with open('streak_block_template_structure.json', 'w') as f:
                json.dump(value_obj, f, indent=2)

            print("📊 STRUCTURE ANALYSIS:")
            print(f"  Top-level keys: {list(value_obj.keys())}")
            print(f"\n  Total campaigns in config: {len(value_obj)}")

            # Check for orphaned campaigns
            orphaned_uuids = [
                "df36a1e6-b8f8-4c57-a64e-6922d010d4c9",  # axis_rupay_10_april
                "6d9fad25-66e9-4750-be8b-a5e9acdc5a24",  # snp_rup_may
                "91187d2d-c738-449d-8cd6-7bd960144248",  # upi_cred_m0_zom
                "4749c643-6b6a-42d1-a9c0-2d9379678284",  # upi_na_zom
                "1519d77d-febc-40dc-bc18-5a25c885247d",  # p2p_na_zom
                "4cc3621b-49c2-4922-9bb4-fa5543261ff6",  # snp_na_zom
                "8936f5a4-e594-4567-8fcb-1925b83e4587",  # rupay_zomato
                "72163f27-a0a3-4fca-b2c6-1c1e7aa47740",  # upi_50_feb
                "508f9e84-38a0-40da-af72-7a2443489df8",  # upi_100_feb
                "1e5cd37a-8aa1-4241-9c5d-fef4917ae303",  # snp_nonrupay_atc
                "fbb8f2d4-2821-4c2d-afc8-73537b45fc09",  # snp_nonrupay_m1_jun
                "5b5e2346-61d1-4ef8-8a4e-9e9ca7203c18",  # upi_activation_25x5_streak
                "9e6130ba-a5a3-4024-a519-dccdcf83ecd6",  # upi_act_20x5_streak
                "7849d4e6-79be-45e2-b7a4-9c1112424b00",  # upi_activation10x3_streak
                "cd8da027-16f7-4c33-8711-2c9d77ee9645",  # upi_activation_10x5_streak
                "35f2b8fd-0baf-48ef-97a1-26b9524312c3",  # unknown_1
                "316f7453-5236-4d43-a3d2-176fd8f5446c"   # unknown_2
            ]

            print(f"\n🔍 ORPHANED CAMPAIGNS FOUND:")
            found_count = 0

            for uuid in orphaned_uuids:
                if uuid in value_obj:
                    found_count += 1
                    block = value_obj[uuid]
                    print(f"\n  UUID: {uuid}")
                    print(f"  Keys in block: {list(block.keys())}")

                    # Check for image URLs
                    has_images = any('image' in str(k).lower() or 'url' in str(k).lower()
                                    for k in block.keys())
                    if has_images:
                        print(f"  ⚠️  HAS IMAGE/URL FIELDS!")
                        for key in block.keys():
                            if 'image' in str(key).lower() or 'url' in str(key).lower():
                                print(f"      - {key}: {block[key]}")

            print(f"\n  Total orphaned campaigns found: {found_count}/17")

            print("\n✓ Saved full structure to: streak_block_template_structure.json")
            print("\n📌 NEXT STEPS:")
            print("  1. Review the saved JSON file to understand block structure")
            print("  2. Determine if we should:")
            print("     a) Remove entire campaign blocks (loses image URLs)")
            print("     b) Keep blocks but mark as inactive/deprecated")
            print("     c) Keep blocks and only remove from other configs")

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse value field as JSON: {str(e)}")
            print(f"  First 500 chars of value: {str(config_data['value'])[:500]}")
    else:
        print("⚠️  No 'value' field found in config")

    print("✓ Saved raw config to: streak_block_template_raw.json")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
