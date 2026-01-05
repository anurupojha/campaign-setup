#!/usr/bin/env python3
"""
Remove 4 activation/reactivation campaigns
"""

import requests
import json
import sys
from typing import Dict, List, Any, Tuple
from retool_integration import load_credentials, HeimdalJourneyConfigAPI, parse_value_field


# Campaigns to remove
CAMPAIGNS_TO_REMOVE = [
    "upi_activation_cred_dormant",
    "upi_activation_cred_mtu_multi_lob",
    "upi_activation_cred_mtu_single_lob",
    "upi_reactivation_cred_dormant"
]


def remove_campaigns(value_obj: Dict[str, Any], campaigns: List[str]) -> Tuple[Dict[str, Any], Dict[str, int]]:
    """Remove campaigns from all 3 sections"""
    counts = {
        'supported_ids': 0,
        'batch_rules': 0,
        'journey_rules': 0
    }

    # 1. Remove from batch_assignment_rules
    batch_rules = value_obj.get('batch_assignment_rules', {})
    configs = batch_rules.get('configs', [])
    original_count = len(configs)

    batch_rules['configs'] = [
        config for config in configs
        if config.get('config_key') not in campaigns
    ]
    counts['batch_rules'] = original_count - len(batch_rules['configs'])
    value_obj['batch_assignment_rules'] = batch_rules

    # 2. Remove from journey_rules
    journey_rules = value_obj.get('journey_rules', {})
    configs = journey_rules.get('configs', [])
    original_count = len(configs)

    journey_rules['configs'] = [
        config for config in configs
        if config.get('config_key') not in campaigns
    ]
    counts['journey_rules'] = original_count - len(journey_rules['configs'])
    value_obj['journey_rules'] = journey_rules

    # 3. No UUIDs to remove from supported_campaign_ids since these only have initial assignment rules

    return value_obj, counts


def main():
    print("\n" + "="*80)
    print("REMOVE 4 ACTIVATION/REACTIVATION CAMPAIGNS")
    print("="*80)

    print(f"\nCampaigns to remove ({len(CAMPAIGNS_TO_REMOVE)}):")
    for i, campaign in enumerate(CAMPAIGNS_TO_REMOVE, 1):
        print(f"  {i}. {campaign}")

    # Load credentials
    userid, apikey = load_credentials()
    if not userid or not apikey:
        print("❌ Error: Could not load credentials")
        sys.exit(1)

    # Initialize API
    api = HeimdalJourneyConfigAPI(userid, apikey)

    # Fetch config
    print(f"\n📡 Fetching STREAK_JOURNEY_JOB_CONFIG...")
    success, config_data, error = api.get_config()
    if not success:
        print(f"❌ Failed: {error}")
        sys.exit(1)
    print("  ✓ Fetched successfully")

    # Parse value
    print(f"\n🔍 Parsing config...")
    success, value_obj, error = parse_value_field(config_data)
    if not success:
        print(f"❌ Failed to parse: {error}")
        sys.exit(1)

    # Show current stats
    print(f"\n📊 BEFORE REMOVAL:")
    print(f"  Supported Campaign IDs: {len(value_obj.get('supported_campaign_ids', []))}")
    print(f"  Batch Assignment Rules: {len(value_obj.get('batch_assignment_rules', {}).get('configs', []))}")
    print(f"  Journey Assignment Rules: {len(value_obj.get('journey_rules', {}).get('configs', []))}")

    # Remove campaigns
    print(f"\n🗑️  Removing campaigns...")
    modified_value_obj, counts = remove_campaigns(value_obj, CAMPAIGNS_TO_REMOVE)

    # Show results
    print(f"\n📊 AFTER REMOVAL:")
    print(f"  Supported Campaign IDs: {len(modified_value_obj.get('supported_campaign_ids', []))} (-{counts['supported_ids']})")
    print(f"  Batch Assignment Rules: {len(modified_value_obj.get('batch_assignment_rules', {}).get('configs', []))} (-{counts['batch_rules']})")
    print(f"  Journey Assignment Rules: {len(modified_value_obj.get('journey_rules', {}).get('configs', []))} (-{counts['journey_rules']})")

    total_removed = sum(counts.values())
    print(f"\n  Total items removed: {total_removed}")

    if total_removed == 0:
        print("\n⚠️  Nothing to remove - campaigns not found or already removed")
        sys.exit(0)

    # Confirm
    print("\n" + "="*80)
    confirm = input("Type 'YES' to proceed with removal: ")

    if confirm != "YES":
        print("\n❌ Removal cancelled")
        sys.exit(0)

    # Update config
    print(f"\n📤 Updating config...")
    config_data['value'] = json.dumps(modified_value_obj, indent=2)
    config_data['updated_by'] = "campaign_cleanup_activation"

    success, message = api.update_config(config_data)

    if success:
        print(f"✅ Success! Removed {total_removed} items from config.")
        print("\n" + "="*80)
        print("CLEANUP COMPLETE")
        print("="*80)
    else:
        print(f"❌ Failed: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
