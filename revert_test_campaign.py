#!/usr/bin/env python3
"""
Revert/Delete Campaign: upi_dormant_140
Campaign ID: d3eb4f15-fbdb-47b1-8092-2ec8076eab52

This script removes the campaign from all configs to allow fresh testing.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from setup_campaign_master import load_credentials, print_header, print_success, print_error, print_info
from retool_integration import HeimdalJourneyConfigAPI, parse_value_field

# Campaign details to remove
CAMPAIGN_NAME = "upi_dormant_140"
CAMPAIGN_ID = "d3eb4f15-fbdb-47b1-8092-2ec8076eab52"

# Configs that need cleanup (UPI campaign has all 6)
CONFIGS_TO_CLEAN = [
    'STREAK_ELIGIBILITY',
    'STREAK_TXN_ELIGIBILITY',
    'STREAK_CONFIG',
    'STREAK_BLOCK_TEMPLATE',
    'SCAN_HOMEPAGE_CONFIG',
    'PTP_STREAK_CONFIG'
]

def remove_from_json_array(data, campaign_name):
    """Remove campaign from a JSON array config"""
    if isinstance(data, dict) and 'value' in data:
        try:
            value_obj = json.loads(data['value'])

            # Handle configs with 'configs' array (STREAK_ELIGIBILITY, STREAK_TXN_ELIGIBILITY, etc.)
            if isinstance(value_obj, dict) and 'configs' in value_obj:
                configs = value_obj['configs']
                original_len = len(configs)
                # Remove entries where config_key matches campaign_name OR starts with campaign_name_
                value_obj['configs'] = [
                    c for c in configs
                    if c.get('config_key') != campaign_name and not c.get('config_key', '').startswith(f"{campaign_name}_")
                ]

                if len(value_obj['configs']) < original_len:
                    data['value'] = json.dumps(value_obj, indent=2)
                    removed_count = original_len - len(value_obj['configs'])
                    return True, f"Removed {removed_count} entries matching '{campaign_name}'"
                else:
                    return False, f"{campaign_name} not found in config"

            # Handle simple array configs
            elif isinstance(value_obj, list):
                original_len = len(value_obj)
                value_obj = [item for item in value_obj if item != campaign_name]

                if len(value_obj) < original_len:
                    data['value'] = json.dumps(value_obj, indent=2)
                    return True, f"Removed {campaign_name}"
                else:
                    return False, f"{campaign_name} not found in config"

        except json.JSONDecodeError as e:
            return False, f"Could not parse config value: {e}"

    return False, "Invalid config structure"


def remove_from_streak_config(data, campaign_id):
    """Remove campaign from STREAK_CONFIG"""
    if isinstance(data, dict) and 'value' in data:
        try:
            value_obj = json.loads(data['value'])

            # STREAK_CONFIG has structure: {"configs": [{"conditions": {"campaign_id": {"value": "..."}}}]}
            if isinstance(value_obj, dict) and 'configs' in value_obj:
                configs = value_obj['configs']
                original_len = len(configs)
                # Remove entries where campaign_id matches
                value_obj['configs'] = [
                    c for c in configs
                    if c.get('conditions', {}).get('campaign_id', {}).get('value') != campaign_id
                ]

                if len(value_obj['configs']) < original_len:
                    data['value'] = json.dumps(value_obj, indent=2)
                    return True, f"Removed campaign_id {campaign_id}"
                else:
                    return False, f"Campaign ID not found"

            # Handle simple list (fallback)
            elif isinstance(value_obj, list):
                original_len = len(value_obj)
                value_obj = [item for item in value_obj if item != campaign_id]

                if len(value_obj) < original_len:
                    data['value'] = json.dumps(value_obj, indent=2)
                    return True, f"Removed campaign_id {campaign_id}"
                else:
                    return False, f"Campaign ID not found"

        except json.JSONDecodeError as e:
            return False, f"Could not parse config: {e}"

    return False, "Invalid config structure"


def remove_from_streak_block_template(data, campaign_id):
    """Remove campaign from STREAK_BLOCK_TEMPLATE (complex - manual check needed)"""
    if isinstance(data, dict) and 'value' in data:
        template = data['value']

        # Check if campaign_id exists in template
        if f'$!campaign_id == "{campaign_id}"' in template:
            print_info(f"Found campaign {campaign_id} in STREAK_BLOCK_TEMPLATE")
            print_error("⚠️  STREAK_BLOCK_TEMPLATE requires MANUAL cleanup!")
            print_info("This is a Velocity template - automated removal is risky.")
            print_info("You need to:")
            print_info(f"  1. Find all instances of: $!campaign_id == \"{campaign_id}\"")
            print_info("  2. Remove the banner URL condition for this campaign")
            print_info("  3. Remove the bottom_sheet block for this campaign")
            return False, "Manual cleanup required"
        else:
            return False, f"Campaign {campaign_id} not found in template"

    return False, "Invalid config structure"


def remove_from_retool_config(api, campaign_name, campaign_id):
    """Remove campaign from STREAK_JOURNEY_JOB_CONFIG"""
    print_header("Cleaning Retool Config")

    # Fetch config
    success, config_data, error = api.get_config()
    if not success:
        print_error(f"Failed to fetch Retool config: {error}")
        return False

    # Parse value
    success, value_obj, error = parse_value_field(config_data)
    if not success:
        print_error(f"Failed to parse Retool config: {error}")
        return False

    # Remove from supported_campaign_ids
    supported_ids = value_obj.get('supported_campaign_ids', [])
    if campaign_id in supported_ids:
        supported_ids.remove(campaign_id)
        print_success(f"Removed {campaign_id} from supported_campaign_ids")

    # Remove from batch_assignment_rules
    batch_rules = value_obj.get('batch_assignment_rules', {}).get('configs', [])
    original_batch_len = len(batch_rules)
    batch_rules = [c for c in batch_rules if c.get('config_key') != campaign_name]
    if len(batch_rules) < original_batch_len:
        value_obj['batch_assignment_rules']['configs'] = batch_rules
        print_success(f"Removed {campaign_name} from batch_assignment_rules")

    # Remove from journey_rules
    journey_rules = value_obj.get('journey_rules', {}).get('configs', [])
    original_journey_len = len(journey_rules)
    journey_rules = [c for c in journey_rules if c.get('config_key') != campaign_name]
    if len(journey_rules) < original_journey_len:
        value_obj['journey_rules']['configs'] = journey_rules
        print_success(f"Removed {campaign_name} from journey_rules")

    # Check if any changes were made
    if (len(supported_ids) < len(value_obj.get('supported_campaign_ids', [])) or
        len(batch_rules) < original_batch_len or
        len(journey_rules) < original_journey_len):

        # Update config
        config_data['value'] = json.dumps(value_obj, indent=2)
        config_data['updated_by'] = f"cleanup_{campaign_name}"

        success, message = api.update_config(config_data)
        if success:
            print_success("✅ Retool config updated successfully!")
            return True
        else:
            print_error(f"Failed to update Retool config: {message}")
            return False
    else:
        print_info("Campaign not found in Retool config")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description=f'Revert campaign: {CAMPAIGN_NAME}')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    args = parser.parse_args()

    print_header(f"Reverting Campaign: {CAMPAIGN_NAME}")
    print_info(f"Campaign ID: {CAMPAIGN_ID}")
    print_info(f"This will remove the campaign from {len(CONFIGS_TO_CLEAN)} configs + Retool")
    print()

    # Load credentials
    credentials = load_credentials()
    if not credentials:
        print_error("No credentials found. Run the main script first.")
        return 1

    userid = credentials['userid']
    apikey = credentials['apikey']

    # Confirm
    if not args.yes:
        response = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print_info("Cancelled")
            return 0

    print()
    print_header("Step 1: Fetch Current Configs")

    import subprocess

    configs_fetched = {}
    for config_key in CONFIGS_TO_CLEAN:
        url = f"http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template/{config_key}"

        curl_cmd = [
            'curl', '-s', '-X', 'GET', url,
            '-H', f'userid: {userid}',
            '-H', f'_cred_apikey: {apikey}'
        ]

        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            configs_fetched[config_key] = data
            print_success(f"Fetched {config_key}")
        except Exception as e:
            print_error(f"Failed to fetch {config_key}: {e}")

    print()
    print_header("Step 2: Remove Campaign from Configs")

    configs_to_post = {}

    for config_key, data in configs_fetched.items():
        if config_key in ['STREAK_ELIGIBILITY', 'STREAK_TXN_ELIGIBILITY',
                          'SCAN_HOMEPAGE_CONFIG', 'PTP_STREAK_CONFIG']:
            # These use campaign_name in arrays
            success, message = remove_from_json_array(data, CAMPAIGN_NAME)
            if success:
                print_success(f"{config_key}: {message}")
                configs_to_post[config_key] = data
            else:
                print_info(f"{config_key}: {message}")

        elif config_key == 'STREAK_CONFIG':
            # Uses campaign_id
            success, message = remove_from_streak_config(data, CAMPAIGN_ID)
            if success:
                print_success(f"{config_key}: {message}")
                configs_to_post[config_key] = data
            else:
                print_info(f"{config_key}: {message}")

        elif config_key == 'STREAK_BLOCK_TEMPLATE':
            # Complex template - needs manual cleanup
            success, message = remove_from_streak_block_template(data, CAMPAIGN_ID)
            if success:
                configs_to_post[config_key] = data
            else:
                print_info(f"{config_key}: {message}")

    if not configs_to_post:
        print_info("No configs need updating")
    else:
        print()
        print_header("Step 3: POST Updated Configs")

        for config_key, data in configs_to_post.items():
            url = "http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template"

            curl_cmd = [
                'curl', '-s', '-X', 'POST', url,
                '-H', 'Content-Type: application/json',
                '-H', f'userid: {userid}',
                '-H', f'_cred_apikey: {apikey}',
                '-d', json.dumps(data)
            ]

            try:
                result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
                print_success(f"✓ Posted {config_key}")
            except Exception as e:
                print_error(f"✗ Failed to post {config_key}: {e}")

    print()
    print_header("Step 4: Clean Retool Config")

    api = HeimdalJourneyConfigAPI(userid, apikey)
    remove_from_retool_config(api, CAMPAIGN_NAME, CAMPAIGN_ID)

    print()
    print_header("✅ Cleanup Complete!")
    print_info("Campaign has been removed from configs")
    print_info("You can now test end-to-end with fresh data")

    return 0


if __name__ == "__main__":
    sys.exit(main())
