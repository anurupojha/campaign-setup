#!/usr/bin/env python3
"""
Show which campaigns the 5 supported UUIDs map to
"""

import requests
import json
import sys
from retool_integration import load_credentials, HeimdalJourneyConfigAPI, parse_value_field


def main():
    print("\n" + "="*80)
    print("VERIFY 5 SUPPORTED CAMPAIGN IDs")
    print("="*80)

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

    # Parse value
    success, value_obj, error = parse_value_field(config_data)
    if not success:
        print(f"❌ Failed to parse: {error}")
        sys.exit(1)

    # Get supported IDs
    supported_ids = value_obj.get('supported_campaign_ids', [])

    print(f"\n📋 SUPPORTED CAMPAIGN IDs: {len(supported_ids)}")
    print()

    # Get all journey rules with campaign_id conditions
    journey_rules = value_obj.get('journey_rules', {}).get('configs', [])

    # Create UUID to campaign name mapping
    uuid_to_campaign = {}
    for config in journey_rules:
        conditions = config.get('conditions', {})
        if 'campaign_id' in conditions:
            uuid = conditions['campaign_id'].get('value')
            campaign_name = config.get('config_key')
            if uuid and campaign_name:
                uuid_to_campaign[uuid] = campaign_name

    # Check each supported UUID
    for i, uuid in enumerate(supported_ids, 1):
        campaign_name = uuid_to_campaign.get(uuid, "⚠️  NOT FOUND IN JOURNEY RULES")

        print(f"  {i}. {uuid}")
        print(f"     → {campaign_name}")

        # Check if it has batch rule
        batch_rules = value_obj.get('batch_assignment_rules', {}).get('configs', [])
        has_batch = any(c.get('config_key') == campaign_name for c in batch_rules)

        # Check if it has journey progression rule
        has_journey = campaign_name in uuid_to_campaign.values()

        markers = []
        if has_batch:
            markers.append("B")
        if has_journey:
            markers.append("J")

        if markers:
            print(f"     [{','.join(markers)}]")
        print()

    # Show campaigns that HAVE journey rules but NO UUID in supported list
    print("\n" + "="*80)
    print("CAMPAIGNS WITH PROGRESSION RULES BUT NO UUID IN SUPPORTED LIST:")
    print("="*80)

    campaigns_with_progression = set(uuid_to_campaign.values())
    campaigns_in_supported = set(uuid_to_campaign.get(uuid) for uuid in supported_ids if uuid in uuid_to_campaign)

    missing = campaigns_with_progression - campaigns_in_supported

    if missing:
        print(f"\n⚠️  Found {len(missing)} campaigns with progression rules but NOT in supported_campaign_ids:")
        for campaign in sorted(missing):
            # Find the UUID
            uuid = next((u for u, c in uuid_to_campaign.items() if c == campaign), None)
            print(f"  - {campaign}")
            print(f"    UUID: {uuid}")
        print("\n❌ ISSUE: These campaigns have journey progression rules but their UUIDs")
        print("   are NOT in supported_campaign_ids. They may not work properly!")
    else:
        print("\n✅ All campaigns with progression rules are in supported_campaign_ids")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal campaigns: {len(set(c.get('config_key') for c in journey_rules))}")
    print(f"Campaigns with progression rules: {len(campaigns_with_progression)}")
    print(f"UUIDs in supported_campaign_ids: {len(supported_ids)}")
    print(f"Match: {len(campaigns_in_supported)}/{len(campaigns_with_progression)}")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
