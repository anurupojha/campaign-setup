#!/usr/bin/env python3
"""
Generate Retool Dashboard Configurations for Campaign Setup

This script generates the 3 JSON configurations needed for Retool:
1. Campaign IDs List
2. Batch Assignment Job
3. Journey Assignment Job

Usage:
    python3 generate_retool_configs.py --campaign-name upi_streak_5 --campaign-id abc-123-xyz

Or run interactively:
    python3 generate_retool_configs.py
"""

import json
import argparse
import sys
from typing import Dict, List, Any


def check_campaign_exists(campaign_id: str, configs: Dict[str, Any]) -> Dict[str, bool]:
    """Check if campaign_id already exists in any of the configs"""
    exists_in = {
        'campaign_ids': False,
        'batch_assignment': False,
        'journey_assignment': False
    }

    # Check in campaign IDs list
    if campaign_id in configs.get('campaign_ids', []):
        exists_in['campaign_ids'] = True

    # Check in batch assignment
    for config in configs.get('batch_assignment', {}).get('configs', []):
        if config.get('config_key') == configs.get('campaign_name'):
            exists_in['batch_assignment'] = True
            break

    # Check in journey assignment
    for config in configs.get('journey_assignment', {}).get('configs', []):
        conditions = config.get('conditions', {})
        campaign_id_cond = conditions.get('campaign_id', {})
        if campaign_id_cond.get('value') == campaign_id:
            exists_in['journey_assignment'] = True
            break

    return exists_in


def add_to_campaign_ids(campaign_id: str, campaign_ids_list: List[str]) -> List[str]:
    """Add campaign_id to the list if not already present"""
    if campaign_id not in campaign_ids_list:
        campaign_ids_list.append(campaign_id)
    return campaign_ids_list


def generate_batch_assignment_block(campaign_name: str) -> Dict[str, Any]:
    """Generate batch assignment config block for a campaign"""
    return {
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


def add_to_batch_assignment(campaign_name: str, batch_config: Dict[str, Any]) -> Dict[str, Any]:
    """Add campaign to batch assignment config"""
    # Find the index of "users_removal_streak_assignment"
    configs = batch_config.get('configs', [])
    insert_index = None

    for i, config in enumerate(configs):
        if config.get('config_key') == 'users_removal_streak_assignment':
            insert_index = i
            break

    # Check if campaign already exists
    campaign_exists = False
    for config in configs:
        if config.get('config_key') == campaign_name:
            campaign_exists = True
            break

    if not campaign_exists:
        new_block = generate_batch_assignment_block(campaign_name)
        if insert_index is not None:
            configs.insert(insert_index, new_block)
        else:
            # Fallback: insert before last config
            configs.insert(-1, new_block)

        batch_config['configs'] = configs

    return batch_config


def generate_journey_assignment_blocks(campaign_name: str, campaign_id: str) -> List[Dict[str, Any]]:
    """Generate journey assignment config blocks for a campaign"""

    # Block 1: Initial assignment (for users in NA streak)
    initial_assignment = {
        "uas_attributes": [
            {
                "attribute": {
                    "name": "heimdall.dynamic_attributes.streak_type",
                    "namespace": "heimdall"
                },
                "value": "NA",
                "operator": "EQ",
                "type": "STRING"
            }
        ],
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

    # Block 2: Progression (after campaign completes → NA)
    progression = {
        "conditions": {
            "campaign_id": {
                "type": "STRING",
                "value": campaign_id,
                "operator": "EQ"
            }
        },
        "config_key": campaign_name,
        "metadata": {
            "next_eligible_streak_type": "NA"
        }
    }

    return [initial_assignment, progression]


def add_to_journey_assignment(campaign_name: str, campaign_id: str, journey_config: Dict[str, Any]) -> Dict[str, Any]:
    """Add campaign to journey assignment config"""
    configs = journey_config.get('configs', [])

    # Check if campaign already exists
    campaign_exists_initial = False
    campaign_exists_progression = False

    for config in configs:
        if config.get('config_key') == campaign_name:
            conditions = config.get('conditions', {})
            if 'assign_next_streak_type' in conditions:
                campaign_exists_initial = True
            if 'campaign_id' in conditions and conditions['campaign_id'].get('value') == campaign_id:
                campaign_exists_progression = True

    # Generate blocks
    blocks = generate_journey_assignment_blocks(campaign_name, campaign_id)
    initial_block, progression_block = blocks

    # Find insertion points
    # Initial assignment: insert before "users_removal_streak_assignment"
    # Progression: insert before "catch_all_condition"

    initial_insert_index = None
    progression_insert_index = None

    for i, config in enumerate(configs):
        if config.get('config_key') == 'users_removal_streak_assignment':
            initial_insert_index = i
        if config.get('config_key') == 'catch_all_condition':
            progression_insert_index = i

    # Add initial assignment block
    if not campaign_exists_initial:
        if initial_insert_index is not None:
            configs.insert(initial_insert_index, initial_block)
            # Adjust progression index if we inserted before it
            if progression_insert_index is not None:
                progression_insert_index += 1
        else:
            # Fallback: insert at a reasonable position (after fraud checks)
            configs.insert(20, initial_block)
            if progression_insert_index is not None:
                progression_insert_index += 1

    # Add progression block
    if not campaign_exists_progression:
        if progression_insert_index is not None:
            configs.insert(progression_insert_index, progression_block)
        else:
            # Fallback: insert before last config
            configs.insert(-1, progression_block)

    journey_config['configs'] = configs
    return journey_config


def generate_retool_configs(campaign_name: str, campaign_id: str,
                           existing_configs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate all 3 Retool configurations for a campaign

    Args:
        campaign_name: Campaign name (e.g., "upi_streak_5")
        campaign_id: Campaign UUID
        existing_configs: Optional dict with existing configs to merge with

    Returns:
        Dict containing all 3 modified configs
    """

    # Initialize with existing or empty configs
    if existing_configs is None:
        existing_configs = {
            'campaign_ids': [],
            'batch_assignment': {'configs': []},
            'journey_assignment': {'configs': []}
        }

    # Check if campaign already exists
    exists_check = check_campaign_exists(campaign_id, {
        'campaign_name': campaign_name,
        'campaign_ids': existing_configs.get('campaign_ids', []),
        'batch_assignment': existing_configs.get('batch_assignment', {}),
        'journey_assignment': existing_configs.get('journey_assignment', {})
    })

    print("\n" + "="*60)
    print("CAMPAIGN EXISTENCE CHECK")
    print("="*60)
    print(f"Campaign Name: {campaign_name}")
    print(f"Campaign ID: {campaign_id}")
    print(f"\nExists in Campaign IDs List: {exists_check['campaign_ids']}")
    print(f"Exists in Batch Assignment: {exists_check['batch_assignment']}")
    print(f"Exists in Journey Assignment: {exists_check['journey_assignment']}")

    if all(exists_check.values()):
        print("\n⚠️  WARNING: Campaign already exists in ALL configs!")
        print("No changes will be made.")
        return existing_configs

    print("\n" + "="*60)
    print("GENERATING CONFIGURATIONS")
    print("="*60)

    # 1. Add to Campaign IDs
    campaign_ids = add_to_campaign_ids(campaign_id, existing_configs.get('campaign_ids', []))
    if not exists_check['campaign_ids']:
        print(f"✓ Added to Campaign IDs list")
    else:
        print(f"- Campaign ID already exists in list")

    # 2. Add to Batch Assignment
    batch_assignment = add_to_batch_assignment(
        campaign_name,
        existing_configs.get('batch_assignment', {'configs': []})
    )
    if not exists_check['batch_assignment']:
        print(f"✓ Added to Batch Assignment")
    else:
        print(f"- Campaign already exists in Batch Assignment")

    # 3. Add to Journey Assignment
    journey_assignment = add_to_journey_assignment(
        campaign_name,
        campaign_id,
        existing_configs.get('journey_assignment', {'configs': []})
    )
    if not exists_check['journey_assignment']:
        print(f"✓ Added to Journey Assignment (2 blocks)")
    else:
        print(f"- Campaign already exists in Journey Assignment")

    return {
        'campaign_ids': campaign_ids,
        'batch_assignment': batch_assignment,
        'journey_assignment': journey_assignment
    }


def save_configs(configs: Dict[str, Any], output_dir: str, campaign_name: str):
    """Save the generated configs to files"""
    import os

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save each config
    with open(f"{output_dir}/campaign_ids.json", 'w') as f:
        json.dump(configs['campaign_ids'], f, indent=2)

    with open(f"{output_dir}/batch_assignment.json", 'w') as f:
        json.dump(configs['batch_assignment'], f, indent=2)

    with open(f"{output_dir}/journey_assignment.json", 'w') as f:
        json.dump(configs['journey_assignment'], f, indent=2)

    print(f"\n✓ Saved configs to: {output_dir}/")
    print(f"  - campaign_ids.json")
    print(f"  - batch_assignment.json")
    print(f"  - journey_assignment.json")


def main():
    parser = argparse.ArgumentParser(description='Generate Retool configs for campaign setup')
    parser.add_argument('--campaign-name', help='Campaign name (e.g., upi_streak_5)')
    parser.add_argument('--campaign-id', help='Campaign UUID')
    parser.add_argument('--mock', action='store_true', help='Run with mock data for testing')

    args = parser.parse_args()

    if args.mock:
        print("\n" + "="*60)
        print("MOCK MODE - Testing with sample data")
        print("="*60)

        # Mock existing configs (empty for testing)
        existing_configs = {
            'campaign_ids': [
                "df36a1e6-b8f8-4c57-a64e-6922d010d4c9",
                "6d9fad25-66e9-4750-be8b-a5e9acdc5a24"
            ],
            'batch_assignment': {
                'configs': [
                    {
                        "config_key": "users_removal_streak_assignment",
                        "conditions": {"assign_next_streak_type": {"type": "STRING", "operator": "EQ", "value": "NA"}},
                        "metadata": {"next_eligible_streak_type": "NA"}
                    }
                ]
            },
            'journey_assignment': {
                'configs': [
                    {
                        "config_key": "users_removal_streak_assignment",
                        "conditions": {"assign_next_streak_type": {"type": "STRING", "operator": "EQ", "value": "NA"}},
                        "metadata": {"next_eligible_streak_type": "NA"}
                    },
                    {
                        "config_key": "catch_all_condition",
                        "metadata": {"next_eligible_streak_type": "NA"}
                    }
                ]
            }
        }

        # Mock campaign data
        campaign_name = "test_campaign_mock"
        campaign_id = "12345678-1234-1234-1234-123456789abc"

        print(f"\nMock Campaign: {campaign_name}")
        print(f"Mock UUID: {campaign_id}")

        # Generate configs
        result = generate_retool_configs(campaign_name, campaign_id, existing_configs)

        # Save to mock output directory
        output_dir = "./mock_retool_output"
        save_configs(result, output_dir, campaign_name)

        print("\n" + "="*60)
        print("MOCK TEST COMPLETE")
        print("="*60)
        print(f"\nReview the generated files in: {output_dir}/")

    else:
        # Interactive or command-line mode
        campaign_name = args.campaign_name
        campaign_id = args.campaign_id

        if not campaign_name or not campaign_id:
            print("\nInteractive Mode")
            print("="*60)
            campaign_name = input("Campaign Name (e.g., upi_streak_5): ").strip()
            campaign_id = input("Campaign UUID: ").strip()

        if not campaign_name or not campaign_id:
            print("Error: Both campaign name and ID are required!")
            sys.exit(1)

        print("\nNote: This script generates configs for NEW campaigns.")
        print("You'll need to provide existing Retool configs to merge with,")
        print("or use --mock mode for testing.")
        print("\nFor now, generating with empty base configs...")

        result = generate_retool_configs(campaign_name, campaign_id)

        # Save to output directory
        output_dir = f"./retool_configs_{campaign_name}"
        save_configs(result, output_dir, campaign_name)


if __name__ == "__main__":
    main()
