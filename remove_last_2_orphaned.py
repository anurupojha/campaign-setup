#!/usr/bin/env python3
"""
Remove the last 2 orphaned UUIDs
"""

import requests
import json
import sys
from retool_integration import load_credentials, HeimdalJourneyConfigAPI, parse_value_field


def main():
    print("\n" + "="*80)
    print("REMOVING LAST 2 ORPHANED UUIDs")
    print("="*80)

    # The 2 remaining orphaned UUIDs
    orphaned = [
        "894fe8e7-832f-4f9c-a869-4977239ca31b",
        "64f3e61b-fe56-4ceb-b936-ec873289a549"
    ]

    print(f"\nRemoving:")
    for uuid in orphaned:
        print(f"  - {uuid}")

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

    # Remove from supported_campaign_ids
    supported_ids = value_obj.get('supported_campaign_ids', [])
    print(f"\nBefore: {len(supported_ids)} supported campaign IDs")

    value_obj['supported_campaign_ids'] = [
        uuid for uuid in supported_ids
        if uuid not in orphaned
    ]

    print(f"After:  {len(value_obj['supported_campaign_ids'])} supported campaign IDs")
    print(f"Removed: {len(supported_ids) - len(value_obj['supported_campaign_ids'])} UUIDs")

    # Update config
    config_data['value'] = json.dumps(value_obj, indent=2)
    config_data['updated_by'] = "campaign_cleanup_final"

    print(f"\n📤 Updating config...")
    success, message = api.update_config(config_data)

    if success:
        print(f"✅ Success! Final cleanup complete.")
    else:
        print(f"❌ Failed: {message}")
        sys.exit(1)

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
