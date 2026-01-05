#!/usr/bin/env python3
"""
Retool Integration for Campaign Setup - CORRECT ARCHITECTURE

This script integrates with the Heimdall API to update:
1. Supported Campaign IDs
2. Batch Assignment Rules
3. Journey Assignment Rules

All three are nested keys within a SINGLE config: STREAK_JOURNEY_JOB_CONFIG
"""

import requests
import json
import sys
from typing import Dict, List, Any, Optional, Tuple


class HeimdalJourneyConfigAPI:
    """Handler for STREAK_JOURNEY_JOB_CONFIG operations"""

    def __init__(self, userid: str, apikey: str):
        self.base_url = "http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template"
        self.config_key = "STREAK_JOURNEY_JOB_CONFIG"
        self.userid = userid
        self.apikey = apikey
        self.headers = {
            'Content-Type': 'application/json',
            'userid': userid,
            '_cred_apikey': apikey
        }

    def get_config(self) -> Tuple[bool, Dict[str, Any], str]:
        """
        Fetch STREAK_JOURNEY_JOB_CONFIG

        Returns:
            (success: bool, config_data: dict, error_message: str)

            config_data contains:
            {
                "key": "STREAK_JOURNEY_JOB_CONFIG",
                "value": "<JSON string>",
                "description": "...",
                "updated_by": "...",
                ...
            }
        """
        url = f"{self.base_url}/{self.config_key}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return True, data, ""

        except requests.exceptions.Timeout:
            return False, {}, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, {}, "Connection error"
        except requests.exceptions.HTTPError as e:
            return False, {}, f"HTTP error {e.response.status_code}: {e.response.text}"
        except Exception as e:
            return False, {}, f"Unexpected error: {str(e)}"

    def update_config(self, config_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update STREAK_JOURNEY_JOB_CONFIG

        Args:
            config_data: Full config object (including key, value, description, etc.)

        Returns:
            (success: bool, message: str)
        """
        url = self.base_url

        try:
            response = requests.post(url, headers=self.headers, json=config_data, timeout=30)
            response.raise_for_status()
            return True, "Successfully updated config"

        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP error {e.response.status_code}: {e.response.text}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"


def parse_value_field(config_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
    """
    Parse the 'value' field from config response

    The 'value' field is a JSON string containing the actual config
    """
    try:
        value_str = config_data.get('value', '{}')
        value_obj = json.loads(value_str)
        return True, value_obj, ""
    except json.JSONDecodeError as e:
        return False, {}, f"Failed to parse value field: {str(e)}"


def check_campaign_exists(campaign_id: str, campaign_name: str,
                          value_obj: Dict[str, Any]) -> Dict[str, bool]:
    """Check if campaign already exists in any of the nested configs"""
    exists_in = {
        'supported_campaigns': False,
        'batch_assignment': False,
        'journey_assignment': False
    }

    # Check in supported_campaign_ids
    campaign_ids = value_obj.get('supported_campaign_ids', [])
    if campaign_id in campaign_ids:
        exists_in['supported_campaigns'] = True

    # Check in batch_assignment_rules
    batch_rules = value_obj.get('batch_assignment_rules', {})
    for config in batch_rules.get('configs', []):
        if config.get('config_key') == campaign_name:
            exists_in['batch_assignment'] = True
            break

    # Check in journey_rules
    journey_rules = value_obj.get('journey_rules', {})
    for config in journey_rules.get('configs', []):
        if config.get('config_key') == campaign_name:
            conditions = config.get('conditions', {})
            if 'campaign_id' in conditions and conditions['campaign_id'].get('value') == campaign_id:
                exists_in['journey_assignment'] = True
                break

    return exists_in


def add_campaign_to_config(campaign_name: str, campaign_id: str,
                           next_campaign: str,
                           value_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add campaign to all 3 nested configs

    Args:
        campaign_name: Campaign name
        campaign_id: Campaign UUID
        next_campaign: Next campaign to chain to (or "NA")
        value_obj: Parsed value object

    Returns:
        Modified value_obj
    """

    # 1. Add to supported_campaign_ids
    campaign_ids = value_obj.get('supported_campaign_ids', [])
    if campaign_id not in campaign_ids:
        campaign_ids.append(campaign_id)
    value_obj['supported_campaign_ids'] = campaign_ids

    # 2. Add to batch_assignment_rules
    batch_rules = value_obj.get('batch_assignment_rules', {'configs': []})
    configs = batch_rules.get('configs', [])

    # Check if already exists
    campaign_exists = any(config.get('config_key') == campaign_name for config in configs)

    if not campaign_exists:
        # Find insertion point (before "users_removal_streak_assignment")
        insert_index = next(
            (i for i, config in enumerate(configs)
             if config.get('config_key') == 'users_removal_streak_assignment'),
            len(configs) - 1
        )

        new_block = {
            "conditions": {
                "assign_next_streak_type": {
                    "type": "STRING",
                    "operator": "EQ",
                    "value": campaign_name
                }
            },
            "config_key": campaign_name,
            "metadata": {
                "next_eligible_streak_type": campaign_name
            }
        }

        configs.insert(insert_index, new_block)
        batch_rules['configs'] = configs
        value_obj['batch_assignment_rules'] = batch_rules

    # 3. Add to journey_rules
    journey_rules = value_obj.get('journey_rules', {'configs': []})
    configs = journey_rules.get('configs', [])

    # Check if blocks already exist
    has_initial = any(
        config.get('config_key') == campaign_name and
        'assign_next_streak_type' in config.get('conditions', {})
        for config in configs
    )

    has_progression = any(
        config.get('config_key') == campaign_name and
        'campaign_id' in config.get('conditions', {}) and
        config['conditions']['campaign_id'].get('value') == campaign_id
        for config in configs
    )

    # Add initial assignment block (no NA check - for manual experiments)
    if not has_initial:
        initial_block = {
            "conditions": {
                "assign_next_streak_type": {
                    "type": "STRING",
                    "operator": "EQ",
                    "value": campaign_name
                }
            },
            "config_key": campaign_name,
            "metadata": {
                "next_eligible_streak_type": campaign_name
            }
        }

        # Insert before "users_removal_streak_assignment"
        insert_index = next(
            (i for i, config in enumerate(configs)
             if config.get('config_key') == 'users_removal_streak_assignment'),
            len(configs) // 2
        )

        configs.insert(insert_index, initial_block)

    # Add progression block
    if not has_progression:
        progression_block = {
            "conditions": {
                "campaign_id": {
                    "type": "STRING",
                    "value": campaign_id,
                    "operator": "EQ"
                }
            },
            "config_key": campaign_name,
            "metadata": {
                "next_eligible_streak_type": next_campaign
            }
        }

        # Insert before "catch_all_condition"
        insert_index = next(
            (i for i, config in enumerate(configs)
             if config.get('config_key') == 'catch_all_condition'),
            len(configs) - 1
        )

        configs.insert(insert_index, progression_block)

    journey_rules['configs'] = configs
    value_obj['journey_rules'] = journey_rules

    return value_obj


def integrate_campaign(campaign_name: str, campaign_id: str,
                       is_chain: bool = False, next_campaign: str = "NA",
                       api: HeimdalJourneyConfigAPI = None,
                       verbose: bool = True) -> Tuple[bool, str]:
    """
    Main function to integrate campaign into Retool configs

    Args:
        campaign_name: Campaign name (e.g., "upi_streak_5")
        campaign_id: Campaign UUID
        is_chain: Whether this campaign chains to another
        next_campaign: Next campaign name (if is_chain=True)
        api: HeimdalJourneyConfigAPI instance
        verbose: Print detailed output

    Returns:
        (success: bool, message: str)
    """

    if verbose:
        print("\n" + "="*60)
        print("RETOOL INTEGRATION")
        print("="*60)
        print(f"Campaign: {campaign_name}")
        print(f"UUID: {campaign_id}")
        print(f"Chain: {'Yes → ' + next_campaign if is_chain else 'No (→ NA)'}")

    try:
        # Step 1: Fetch config
        if verbose:
            print("\n📡 Fetching STREAK_JOURNEY_JOB_CONFIG from Heimdall...")

        success, config_data, error = api.get_config()
        if not success:
            return False, f"Failed to fetch config: {error}"

        if verbose:
            print("  ✓ Fetched config successfully")

        # Step 2: Parse value field
        if verbose:
            print("\n🔍 Parsing config value...")

        success, value_obj, error = parse_value_field(config_data)
        if not success:
            return False, f"Failed to parse config: {error}"

        if verbose:
            print(f"  ✓ Parsed config")
            print(f"    - Supported campaigns: {len(value_obj.get('supported_campaign_ids', []))}")
            print(f"    - Batch rules: {len(value_obj.get('batch_assignment_rules', {}).get('configs', []))} configs")
            print(f"    - Journey rules: {len(value_obj.get('journey_rules', {}).get('configs', []))} configs")

        # Step 3: Check if campaign already exists
        if verbose:
            print("\n🔍 Checking for duplicates...")

        exists = check_campaign_exists(campaign_id, campaign_name, value_obj)

        if all(exists.values()):
            if verbose:
                print("  ⚠️  Campaign already exists in ALL configs!")
            return True, "Campaign already configured (skipped)"

        if any(exists.values()):
            if verbose:
                print(f"  ⚠️  Partial existence detected:")
                for config_name, exists_flag in exists.items():
                    print(f"     - {config_name}: {'EXISTS' if exists_flag else 'NOT FOUND'}")
                print("  → Will add to missing configs only")
        else:
            if verbose:
                print("  ✓ Campaign not found (will add)")

        # Step 4: Add campaign to configs
        if verbose:
            print("\n⚙️  Updating configs...")

        next_camp = next_campaign if is_chain else "NA"
        modified_value_obj = add_campaign_to_config(campaign_name, campaign_id,
                                                     next_camp, value_obj)

        if verbose:
            if not exists['supported_campaigns']:
                print("  ✓ Added to supported campaigns")
            if not exists['batch_assignment']:
                print("  ✓ Added to batch assignment")
            if not exists['journey_assignment']:
                print(f"  ✓ Added to journey assignment (→ {next_camp})")

        # Step 5: Prepare payload for POST
        if verbose:
            print("\n📦 Preparing payload...")

        # Stringify the modified value object
        modified_value_str = json.dumps(modified_value_obj, indent=2)

        # Update the config_data with new value
        config_data['value'] = modified_value_str
        config_data['updated_by'] = "campaign_setup_automation"

        # Step 6: POST back to API
        if verbose:
            print("\n📤 Posting updated config to Heimdall...")

        success, message = api.update_config(config_data)
        if not success:
            return False, f"Failed to update config: {message}"

        if verbose:
            print("  ✓ Config updated successfully")
            print("\n" + "="*60)
            print("✨ RETOOL INTEGRATION COMPLETE!")
            print("="*60)

        return True, "Successfully integrated campaign into Retool"

    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def load_credentials(creds_file: str = "./credentials.json") -> Tuple[Optional[str], Optional[str]]:
    """Load API credentials from file"""
    try:
        with open(creds_file, 'r') as f:
            creds = json.load(f)
            return creds.get('userid'), creds.get('apikey')
    except FileNotFoundError:
        return None, None
    except json.JSONDecodeError:
        return None, None


def main():
    """Test the Retool integration"""
    import argparse

    parser = argparse.ArgumentParser(description='Integrate campaign into Retool configs')
    parser.add_argument('--campaign-name', required=True, help='Campaign name')
    parser.add_argument('--campaign-id', required=True, help='Campaign UUID')
    parser.add_argument('--chain', action='store_true', help='Is this a chain streak?')
    parser.add_argument('--next-campaign', default='NA', help='Next campaign name (if chain)')
    parser.add_argument('--test', action='store_true', help='Test mode (fetch only, no POST)')

    args = parser.parse_args()

    # Load credentials
    userid, apikey = load_credentials()
    if not userid or not apikey:
        print("❌ Error: Could not load credentials from credentials.json")
        sys.exit(1)

    # Initialize API
    api = HeimdalJourneyConfigAPI(userid, apikey)

    if args.test:
        print("\n" + "="*60)
        print("TEST MODE - Fetch Only")
        print("="*60)

        print("\n📡 Testing GET endpoint...")
        success, config_data, error = api.get_config()

        if success:
            print("  ✓ Success! Fetched config")

            # Parse value
            success, value_obj, error = parse_value_field(config_data)
            if success:
                print(f"\n📊 Config Statistics:")
                print(f"  - Supported campaigns: {len(value_obj.get('supported_campaign_ids', []))}")
                print(f"  - Batch rules: {len(value_obj.get('batch_assignment_rules', {}).get('configs', []))} configs")
                print(f"  - Journey rules: {len(value_obj.get('journey_rules', {}).get('configs', []))} configs")

                # Check if campaign exists
                exists = check_campaign_exists(args.campaign_id, args.campaign_name, value_obj)
                print(f"\n🔍 Campaign Check:")
                print(f"  - Supported campaigns: {'EXISTS' if exists['supported_campaigns'] else 'NOT FOUND'}")
                print(f"  - Batch assignment: {'EXISTS' if exists['batch_assignment'] else 'NOT FOUND'}")
                print(f"  - Journey assignment: {'EXISTS' if exists['journey_assignment'] else 'NOT FOUND'}")
            else:
                print(f"  ❌ Failed to parse value: {error}")
        else:
            print(f"  ❌ Failed: {error}")

        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
    else:
        # Run full integration
        success, message = integrate_campaign(
            args.campaign_name,
            args.campaign_id,
            args.chain,
            args.next_campaign,
            api,
            verbose=True
        )

        if success:
            print(f"\n✅ {message}")
            sys.exit(0)
        else:
            print(f"\n❌ {message}")
            sys.exit(1)


if __name__ == "__main__":
    main()
