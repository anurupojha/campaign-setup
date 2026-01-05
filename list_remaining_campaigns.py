#!/usr/bin/env python3
"""
List all remaining campaigns after cleanup
"""

import requests
import json
import sys
from typing import Dict, List, Any, Tuple
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
    print("REMAINING CAMPAIGNS AFTER CLEANUP")
    print("="*80)

    # Load credentials
    userid, apikey = load_credentials()
    if not userid or not apikey:
        print("❌ Error: Could not load credentials")
        sys.exit(1)

    # Fetch STREAK_JOURNEY_JOB_CONFIG
    print("\n📡 Fetching STREAK_JOURNEY_JOB_CONFIG...")
    config_data = fetch_config("STREAK_JOURNEY_JOB_CONFIG", userid, apikey)

    # Parse value
    try:
        value_obj = json.loads(config_data['value'])
    except:
        print("❌ Failed to parse config")
        sys.exit(1)

    # Get all sections
    supported_ids = value_obj.get('supported_campaign_ids', [])
    batch_rules = value_obj.get('batch_assignment_rules', {}).get('configs', [])
    journey_rules = value_obj.get('journey_rules', {}).get('configs', [])

    print(f"\n📊 STATISTICS:")
    print(f"  Supported Campaign IDs: {len(supported_ids)}")
    print(f"  Batch Assignment Rules: {len(batch_rules)}")
    print(f"  Journey Assignment Rules: {len(journey_rules)}")

    # Extract campaign names from batch rules
    batch_campaigns = []
    for config in batch_rules:
        config_key = config.get('config_key', '')
        if config_key and config_key != 'users_removal_streak_assignment':
            batch_campaigns.append(config_key)

    # Extract campaign names from journey rules
    journey_campaigns = []
    for config in journey_rules:
        config_key = config.get('config_key', '')
        if config_key and config_key not in ['users_removal_streak_assignment', 'catch_all_condition']:
            journey_campaigns.append(config_key)

    # Get unique campaign names
    all_campaign_names = sorted(set(batch_campaigns + journey_campaigns))

    print(f"\n📋 DISTINCT CAMPAIGN NAMES WITH RULES: {len(all_campaign_names)}")
    print()
    for i, name in enumerate(all_campaign_names, 1):
        # Check if in both batch and journey
        in_batch = name in batch_campaigns
        in_journey = name in journey_campaigns

        markers = []
        if in_batch:
            markers.append("B")
        if in_journey:
            markers.append("J")

        marker_str = f"[{','.join(markers)}]"
        print(f"  {i:2d}. {name:50s} {marker_str}")

    print("\nLegend:")
    print("  [B]   = Has Batch Assignment Rule")
    print("  [J]   = Has Journey Assignment Rule")
    print("  [B,J] = Has Both")

    # Check for orphans (should be 0 now)
    orphaned = [uuid for uuid in supported_ids
                if not any(uuid in str(config) for config in batch_rules)
                and not any(uuid in str(config) for config in journey_rules)]

    if orphaned:
        print(f"\n⚠️  WARNING: Still have {len(orphaned)} orphaned UUIDs!")
        for uuid in orphaned[:5]:
            print(f"    - {uuid}")
    else:
        print(f"\n✅ No orphaned UUIDs - all supported_campaign_ids have rules!")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
