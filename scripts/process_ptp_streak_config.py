#!/usr/bin/env python3
"""
Process PTP_STREAK_CONFIG
Adds new campaign configs to the P2P (peer-to-peer) home screen.

NOTE: This config is ONLY for UPI and P2P campaigns.
      SNP (scan & pay only) campaigns do NOT need this config.

Usage:
    python3 process_ptp_streak_config.py \
        <before_json_path> \
        <after_unescaped_path> \
        <after_json_path> \
        <campaign_name> \
        <campaign_type> \
        <duration_days> \
        <max_allowed> \
        <per_txn_reward> \
        <total_offer>

Example:
    python3 process_ptp_streak_config.py \
        PTP_STREAK_CONFIG_before.json \
        PTP_STREAK_CONFIG_after_unescaped.json \
        PTP_STREAK_CONFIG_after.json \
        upi_test_campaign \
        UPI \
        14 \
        5 \
        10 \
        50
"""

import json
import sys


# Standard search.data array used across all configs
STANDARD_SEARCH_DATA = [
    {
        "text": "pay to",
        "right_asset": {
            "url": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/6b23258061e311eeaa853f670a0e3012.svg",
            "type": "svg",
            "aspect_ratio": 1
        }
    },
    {
        "text": "pay to",
        "right_asset": {
            "url": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/6325b4b061e311eeaa853f670a0e3012.svg",
            "type": "svg",
            "aspect_ratio": 1
        }
    },
    {
        "text": "pay to",
        "right_asset": {
            "url": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/5c5c08f061e311eeaa853f670a0e3012.svg",
            "type": "svg",
            "aspect_ratio": 1
        }
    },
    {
        "text": "pay to",
        "right_asset": {
            "url": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/4ab46e30629211eea0ed0bd74220cbfb.png",
            "type": "image",
            "aspect_ratio": 1
        }
    },
    {
        "text": "pay via",
        "right_asset": {
            "url": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/eb8447a0627311eebf66138229c45306.svg",
            "type": "svg",
            "aspect_ratio": 1.823
        }
    },
    {
        "text": "pay to contacts",
        "right_asset": None
    },
    {
        "text": "pay to phone number",
        "right_asset": None
    }
]


def find_insertion_index(configs):
    """
    Find insertion point: insert BEFORE p2p_default (fallback config).
    Fallback to p2p_0_state if p2p_default not found.
    """
    fallback_markers = ['p2p_default', 'p2p_0_state']

    for marker in fallback_markers:
        for i, config in enumerate(configs):
            if config.get('config_key') == marker:
                return i

    # Last resort: append at end
    return len(configs)


def create_initial_config(campaign_name, campaign_type, duration_days, total_offer, max_allowed):
    """
    Create _0 config (initial state, no transactions yet).

    KEY DIFFERENCE from SCAN_HOMEPAGE_CONFIG:
    - Has BOTH text array AND streak_text field
    """
    return {
        "config_key": f"{campaign_name}_0",
        "uas_attributes": [
            {
                "attribute": {
                    "namespace": "heimdall",
                    "name": "heimdall.dynamic_attributes.streak_type"
                },
                "type": "STRING",
                "operator": "IN",
                "value": [campaign_name]
            }
        ],
        "conditions": {
            "type": {
                "type": "STRING",
                "operator": "EQ",
                "value": campaign_type
            },
            "status": {
                "type": "STRING",
                "operator": "IN",
                "value": ["IN_PROGRESS", "ELIGIBLE"]
            }
        },
        "metadata": {
            "cta": {
                "asset": {
                    "url": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/snp_gallery_icon.svg",
                    "type": "svg"
                },
                "type": "DEEPLINK",
                "action": "cred://app/launch?target=scan_pay&source=p2p_home_screen"
            },
            "carousel": {
                "duration": 2000,
                "interval": 2000,
                "turns": 8,
                "timer_threshold": 172800000,
                "streak_text": "ENDS IN <expiry_timer>",
                "text": [
                    f"<format>assured <icon>INR</icon>{total_offer} cashback on {max_allowed} UPI payments</format>",
                    f"<format>offer expires in {duration_days} days</format>"
                ]
            },
            "search": {
                "data": STANDARD_SEARCH_DATA,
                "interval": 1000,
                "turns": 15
            },
            "config": {
                "show_streak": True,
                "forward_streak_data": True,
                "forward_offer_nudge_data": True
            }
        }
    }


def create_inprogress_config(campaign_name, campaign_type, max_allowed, per_txn_reward):
    """
    Create _1_X config (in-progress state, 1+ transactions completed).
    """
    return {
        "config_key": f"{campaign_name}_1_{max_allowed}",
        "uas_attributes": [
            {
                "attribute": {
                    "namespace": "heimdall",
                    "name": "heimdall.dynamic_attributes.streak_type"
                },
                "type": "STRING",
                "operator": "IN",
                "value": [campaign_name]
            }
        ],
        "conditions": {
            "type": {
                "type": "STRING",
                "operator": "EQ",
                "value": campaign_type
            },
            "status": {
                "type": "STRING",
                "operator": "IN",
                "value": ["IN_PROGRESS", "ELIGIBLE"]
            },
            "completed": {
                "type": "NUMBER",
                "operator": "GTE",
                "value": 1
            }
        },
        "metadata": {
            "cta": {
                "asset": {
                    "url": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/snp_gallery_icon.svg",
                    "type": "svg"
                },
                "type": "DEEPLINK",
                "action": "cred://app/launch?target=scan_pay&source=p2p_home_screen"
            },
            "carousel": {
                "duration": 2000,
                "interval": 2000,
                "turns": 8,
                "timer_threshold": 172800000,
                "streak_text": "ENDS IN <expiry_timer>",
                "offer_text": f"<format>assured <icon>INR</icon>{per_txn_reward} cashback on next UPI payment</format>"
            },
            "search": {
                "data": STANDARD_SEARCH_DATA,
                "interval": 1000,
                "turns": 15
            },
            "config": {
                "show_streak": True,
                "forward_streak_data": True,
                "forward_offer_nudge_data": True
            }
        }
    }


def main():
    if len(sys.argv) != 10:
        print(__doc__)
        sys.exit(1)

    before_json_path = sys.argv[1]
    after_unescaped_path = sys.argv[2]
    after_json_path = sys.argv[3]
    campaign_name = sys.argv[4]
    campaign_type = sys.argv[5]
    duration_days = int(sys.argv[6])
    max_allowed = int(sys.argv[7])
    per_txn_reward = int(sys.argv[8])
    total_offer = int(sys.argv[9])

    # Validate campaign type
    if campaign_type not in ['UPI', 'P2P']:
        print(f"ERROR: PTP_STREAK_CONFIG only supports UPI and P2P campaigns!")
        print(f"       Campaign type '{campaign_type}' is not supported.")
        print(f"       SNP campaigns should skip this config.")
        sys.exit(1)

    # Read original config
    with open(before_json_path, 'r') as f:
        data = json.load(f)

    # Unescape value
    value_str = data['value']
    value_unescaped = json.loads(value_str)

    # Find insertion index
    insertion_idx = find_insertion_index(value_unescaped['configs'])

    print(f"Processing PTP_STREAK_CONFIG for: {campaign_name}")
    print(f"  Campaign type: {campaign_type}")
    print(f"  Duration: {duration_days} days")
    print(f"  Max allowed: {max_allowed}")
    print(f"  Insertion index: {insertion_idx}")

    # Create new configs (always 2 for UPI/P2P campaigns)
    print(f"  Creating 2 configs: {campaign_name}_0 and {campaign_name}_1_{max_allowed}")

    new_configs = [
        create_initial_config(campaign_name, campaign_type, duration_days, total_offer, max_allowed),
        create_inprogress_config(campaign_name, campaign_type, max_allowed, per_txn_reward)
    ]

    # Insert at correct position
    for i, new_config in enumerate(new_configs):
        value_unescaped['configs'].insert(insertion_idx + i, new_config)

    # Save unescaped version
    with open(after_unescaped_path, 'w') as f:
        json.dump(value_unescaped, f, indent=2)

    print(f"  ✓ Saved unescaped: {after_unescaped_path}")

    # Re-escape value
    data['value'] = json.dumps(value_unescaped, separators=(',', ':')).replace('\n', '\\r\\n')

    # Save final version
    with open(after_json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"  ✓ Saved escaped: {after_json_path}")
    print(f"  ✓ Total configs: {len(value_unescaped['configs'])}")
    print(f"\n✓ PTP_STREAK_CONFIG processing complete!")


if __name__ == "__main__":
    main()
