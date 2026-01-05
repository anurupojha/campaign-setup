#!/usr/bin/env python3
"""
Show journey rules for specific campaigns
"""

import requests
import json
import sys
from retool_integration import load_credentials, HeimdalJourneyConfigAPI, parse_value_field


def main():
    campaigns = [
        "upi_25x1_streak",
        "snp_flat_10_multilob_act_react",
        "cred_mtu_single_lob_others_retention"
    ]

    print("\n" + "="*80)
    print("JOURNEY RULES FOR 3 BATCH JOBS")
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

    # Get journey rules
    journey_rules = value_obj.get('journey_rules', {}).get('configs', [])

    # Find rules for these campaigns
    for campaign in campaigns:
        print(f"\n{'='*80}")
        print(f"CAMPAIGN: {campaign}")
        print('='*80)

        found_rules = [
            config for config in journey_rules
            if config.get('config_key') == campaign
        ]

        if not found_rules:
            print("  ⚠️  No journey rules found")
            continue

        print(f"\n  Found {len(found_rules)} journey rule(s):\n")

        for i, rule in enumerate(found_rules, 1):
            print(f"  Rule #{i}:")
            print(f"  ----------")

            # Show conditions
            conditions = rule.get('conditions', {})
            if conditions:
                print(f"  Conditions:")
                for key, val in conditions.items():
                    if isinstance(val, dict):
                        print(f"    - {key}:")
                        print(f"        type: {val.get('type')}")
                        print(f"        operator: {val.get('operator')}")
                        print(f"        value: {val.get('value')}")
                    else:
                        print(f"    - {key}: {val}")

            # Show UAS attributes
            uas_attrs = rule.get('uas_attributes', [])
            if uas_attrs:
                print(f"  UAS Attributes:")
                for attr in uas_attrs:
                    attr_name = attr.get('attribute', {}).get('name', '')
                    attr_value = attr.get('value', '')
                    attr_op = attr.get('operator', '')
                    print(f"    - {attr_name} {attr_op} '{attr_value}'")

            # Show metadata (next campaign)
            metadata = rule.get('metadata', {})
            if metadata:
                next_campaign = metadata.get('next_eligible_streak_type', '')
                print(f"  Next Campaign: {next_campaign}")

            print()

    print("="*80)


if __name__ == "__main__":
    main()
