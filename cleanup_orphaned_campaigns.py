#!/usr/bin/env python3
"""
SAFE CLEANUP: Remove 17 orphaned campaigns from 6 configs
(SKIPS STREAK_BLOCK_TEMPLATE to preserve image URLs)
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from retool_integration import load_credentials


# The 17 orphaned campaigns to remove
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

# Configs to clean (EXCLUDING STREAK_BLOCK_TEMPLATE)
CONFIGS_TO_CLEAN = {
    "STREAK_ELIGIBILITY": "remove_campaign_names",
    "STREAK_TXN_ELIGIBILITY": "remove_campaign_names",
    "STREAK_CONFIG": "remove_uuids",
    "SCAN_HOMEPAGE_CONFIG": "remove_campaign_names",
    "PTP_STREAK_CONFIG": "remove_campaign_names",
    "STREAK_JOURNEY_JOB_CONFIG": "remove_uuids"
}


def fetch_config(config_key: str, userid: str, apikey: str) -> Tuple[bool, Dict, str]:
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
        return True, response.json(), ""
    except Exception as e:
        return False, {}, str(e)


def update_config(config_key: str, config_data: Dict, userid: str, apikey: str) -> Tuple[bool, str]:
    """Update a Heimdall config"""
    base_url = "http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template"
    url = base_url
    headers = {
        'Content-Type': 'application/json',
        'userid': userid,
        '_cred_apikey': apikey
    }

    try:
        response = requests.post(url, headers=headers, json=config_data, timeout=30)
        response.raise_for_status()
        return True, "Success"
    except Exception as e:
        return False, str(e)


def backup_configs(configs: Dict[str, Dict], backup_dir: str):
    """Backup all configs to JSON files"""
    os.makedirs(backup_dir, exist_ok=True)

    for config_key, config_data in configs.items():
        backup_file = os.path.join(backup_dir, f"{config_key}.json")
        with open(backup_file, 'w') as f:
            json.dump(config_data, f, indent=2)

    print(f"✓ Backed up {len(configs)} configs to: {backup_dir}")


def remove_from_json_value(value_str: str, remove_type: str) -> Tuple[str, List[str]]:
    """Remove orphaned campaigns from a JSON value field"""
    try:
        value_obj = json.loads(value_str)
    except:
        return value_str, []

    removed = []

    if remove_type == "remove_campaign_names":
        # Search recursively for arrays containing campaign names
        def clean_obj(obj):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    obj[key] = clean_obj(val)
            elif isinstance(obj, list):
                # Only filter string items, keep non-string items as-is
                new_list = []
                for item in obj:
                    if isinstance(item, str) and item in ORPHANED_CAMPAIGNS.keys():
                        removed.append(item)
                    else:
                        new_list.append(clean_obj(item) if not isinstance(item, str) else item)
                obj[:] = new_list
            return obj

        value_obj = clean_obj(value_obj)

    elif remove_type == "remove_uuids":
        # For STREAK_CONFIG and STREAK_JOURNEY_JOB_CONFIG
        if isinstance(value_obj, dict):
            # Remove from supported_campaign_ids array
            if 'supported_campaign_ids' in value_obj and isinstance(value_obj['supported_campaign_ids'], list):
                original = value_obj['supported_campaign_ids'].copy()
                value_obj['supported_campaign_ids'] = [
                    uuid for uuid in value_obj['supported_campaign_ids']
                    if uuid not in ORPHANED_CAMPAIGNS.values()
                ]
                removed = [uuid for uuid in original if uuid not in value_obj['supported_campaign_ids']]

            # Remove UUID keys from top level (for STREAK_CONFIG)
            keys_to_remove = [k for k in value_obj.keys() if k in ORPHANED_CAMPAIGNS.values()]
            for key in keys_to_remove:
                del value_obj[key]
                removed.append(key)

        elif isinstance(value_obj, list):
            # Remove UUIDs from array
            original = value_obj.copy()
            value_obj[:] = [uuid for uuid in value_obj if uuid not in ORPHANED_CAMPAIGNS.values()]
            removed = [uuid for uuid in original if uuid not in value_obj]

    return json.dumps(value_obj, indent=2), removed


def analyze_cleanup(configs: Dict[str, Dict]) -> Dict[str, List[str]]:
    """Analyze what will be removed from each config"""
    analysis = {}

    for config_key, remove_type in CONFIGS_TO_CLEAN.items():
        if config_key not in configs:
            continue

        config_data = configs[config_key]
        if 'value' not in config_data:
            continue

        _, removed = remove_from_json_value(config_data['value'], remove_type)
        if removed:
            analysis[config_key] = removed

    return analysis


def perform_cleanup(configs: Dict[str, Dict], userid: str, apikey: str, dry_run: bool = True) -> Dict[str, bool]:
    """Perform the cleanup"""
    results = {}

    for config_key, remove_type in CONFIGS_TO_CLEAN.items():
        if config_key not in configs:
            print(f"\n⚠️  {config_key}: Not found, skipping")
            results[config_key] = False
            continue

        config_data = configs[config_key]
        if 'value' not in config_data:
            print(f"\n⚠️  {config_key}: No value field, skipping")
            results[config_key] = False
            continue

        print(f"\n🔧 Processing {config_key}...")

        # Remove orphaned campaigns
        new_value, removed = remove_from_json_value(config_data['value'], remove_type)

        if not removed:
            print(f"  ℹ️  Nothing to remove")
            results[config_key] = True
            continue

        print(f"  → Will remove {len(removed)} items")
        for item in removed[:5]:  # Show first 5
            display = item[:40] + "..." if len(item) > 40 else item
            print(f"    - {display}")
        if len(removed) > 5:
            print(f"    ... and {len(removed) - 5} more")

        if dry_run:
            print(f"  ⏸️  DRY RUN - no changes made")
            results[config_key] = True
        else:
            # Update config
            config_data['value'] = new_value
            config_data['updated_by'] = "campaign_cleanup_automation"

            success, message = update_config(config_key, config_data, userid, apikey)
            if success:
                print(f"  ✓ Updated successfully")
                results[config_key] = True
            else:
                print(f"  ❌ Update failed: {message}")
                results[config_key] = False

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Clean up orphaned campaigns from Heimdall configs')
    parser.add_argument('--execute', action='store_true', help='Execute cleanup (default is dry-run)')
    parser.add_argument('--skip-backup', action='store_true', help='Skip backup step')
    args = parser.parse_args()

    print("\n" + "="*80)
    print("SAFE CLEANUP: Remove 17 Orphaned Campaigns")
    print("="*80)
    print("\n⚠️  IMPORTANT: This script SKIPS STREAK_BLOCK_TEMPLATE to preserve image URLs")
    print(f"\nMode: {'🔴 EXECUTE (WILL MODIFY PROD)' if args.execute else '🟢 DRY RUN (safe, read-only)'}")
    print(f"Configs to clean: {len(CONFIGS_TO_CLEAN)}")
    print(f"Campaigns to remove: {len(ORPHANED_CAMPAIGNS)}\n")

    # Load credentials
    userid, apikey = load_credentials()
    if not userid or not apikey:
        print("❌ Error: Could not load credentials")
        sys.exit(1)

    # Fetch all configs
    print("📡 Fetching configs...")
    configs = {}

    for config_key in CONFIGS_TO_CLEAN.keys():
        print(f"  - {config_key}...", end=" ")
        success, config_data, error = fetch_config(config_key, userid, apikey)
        if success:
            configs[config_key] = config_data
            print("✓")
        else:
            print(f"❌ {error}")

    if len(configs) != len(CONFIGS_TO_CLEAN):
        print(f"\n⚠️  Warning: Only fetched {len(configs)}/{len(CONFIGS_TO_CLEAN)} configs")

    # Backup
    if not args.skip_backup:
        print(f"\n💾 Creating backups...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"./config_backups_{timestamp}"
        backup_configs(configs, backup_dir)

    # Analyze
    print(f"\n🔍 Analyzing cleanup impact...")
    analysis = analyze_cleanup(configs)

    print("\n" + "="*80)
    print("CLEANUP PREVIEW")
    print("="*80)

    total_removals = sum(len(items) for items in analysis.values())
    print(f"\nTotal items to remove: {total_removals}")

    for config_key, removed_items in analysis.items():
        print(f"\n{config_key}: {len(removed_items)} items")
        for item in removed_items[:3]:
            display = item[:60] + "..." if len(item) > 60 else item
            print(f"  - {display}")
        if len(removed_items) > 3:
            print(f"  ... and {len(removed_items) - 3} more")

    # Confirm
    if args.execute:
        print("\n" + "="*80)
        print("⚠️  WARNING: YOU ARE ABOUT TO MODIFY PRODUCTION CONFIGS!")
        print("="*80)
        confirm = input("\nType 'YES' to proceed with cleanup: ")

        if confirm != "YES":
            print("\n❌ Cleanup cancelled")
            sys.exit(0)

        print("\n🔴 EXECUTING CLEANUP...")
        results = perform_cleanup(configs, userid, apikey, dry_run=False)

        # Summary
        print("\n" + "="*80)
        print("CLEANUP COMPLETE")
        print("="*80)

        success_count = sum(1 for v in results.values() if v)
        print(f"\n✓ Successfully cleaned: {success_count}/{len(results)} configs")

        if success_count < len(results):
            print(f"\n⚠️  Failed configs:")
            for config_key, success in results.items():
                if not success:
                    print(f"  - {config_key}")

    else:
        print("\n" + "="*80)
        print("DRY RUN COMPLETE - No changes made")
        print("="*80)
        print("\nTo execute cleanup, run:")
        print("  python3 cleanup_orphaned_campaigns.py --execute")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
