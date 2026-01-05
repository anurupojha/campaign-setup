#!/usr/bin/env python3
"""
Process SCAN_HOMEPAGE_CONFIG
Adds new campaign configs to the scan homepage carousel.

Usage:
    python3 process_scan_homepage_config.py \
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
    python3 process_scan_homepage_config.py \
        SCAN_HOMEPAGE_CONFIG_before.json \
        SCAN_HOMEPAGE_CONFIG_after_unescaped.json \
        SCAN_HOMEPAGE_CONFIG_after.json \
        upi_streak_5 \
        SNP \
        14 \
        5 \
        10 \
        50
"""

import json
import sys
import copy


def find_insertion_index(configs):
    """
    Find insertion point with cascading fallbacks.
    Try each system config marker in order until one is found.
    Insert BEFORE the first one found.
    """
    system_config_order = [
        'widget_assured_20_and',      # Try first
        'widget_assured_20_ios',      # Fallback 1
        'widget_campaign_and',        # Fallback 2
        'widget_campaign_ios',        # Fallback 3
        'wr_pay_ios',                 # Fallback 4
        'wr_pay_android',             # Fallback 5
        'snp_catch_all'               # Fallback 6 (catch-all - should always exist)
    ]

    for marker in system_config_order:
        for i, config in enumerate(configs):
            if config.get('config_key') == marker:
                return i  # Insert BEFORE this config

    # Last resort: append at end (if all 7 system configs removed - unlikely)
    return len(configs)


def create_initial_config(campaign_name, campaign_type, duration_days, total_offer, max_allowed):
    """
    Create _0 config (initial state, no transactions yet).
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
            "carousel": {
                "duration": 2000,
                "interval": 2000,
                "turns": 8,
                "timer_threshold": 172800000,
                "text": [
                    f"<format>assured cashback of <icon>INR</icon>{total_offer} on next {max_allowed} payments</format>",
                    f"offer expires in {duration_days} days"
                ],
                "timer_prefix_asset": {}
            },
            "search": {
                "left_asset": {
                    "url": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/search_icon",
                    "type": "svg"
                },
                "text": "<format>search & pay contacts</format>",
                "border_animation_count": 2,
                "cta": {
                    "type": "p2p_home",
                    "additional_info": {
                        "search_phone_num_keyboard": True,
                        "headers": {},
                        "offer_nudge": {
                            "asset": {}
                        }
                    }
                },
                "right_asset": {
                    "asset": {}
                }
            },
            "config": {
                "show_streak": True,
                "forward_streak_data": True,
                "forward_offer_nudge_data": True
            },
            "cta": {}
        }
    }


def create_inprogress_config(campaign_name, campaign_type, max_allowed, per_txn_reward):
    """
    Create _1_X config (in-progress state, 1+ transactions completed).
    """
    # Campaign-type aware copy
    payment_text = "scan & pay" if campaign_type == "SNP" else "UPI payment"

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
            "carousel": {
                "duration": 2000,
                "interval": 2000,
                "turns": 8,
                "timer_threshold": 172800000,
                "streak_text": "ends in <expiry_timer>",
                "offer_text": f"<format>assured <icon>INR</icon>{per_txn_reward} cashback on next {payment_text}</format>"
            },
            "search": {
                "left_asset": {
                    "url": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/search_icon",
                    "type": "svg"
                },
                "text": "<format>search & pay contacts</format>",
                "right_asset": {
                    "text": "CASHBACK"
                },
                "border_animation_count": 2,
                "cta": {
                    "type": "p2p_home",
                    "additional_info": {
                        "search_phone_num_keyboard": True
                    }
                }
            },
            "config": {
                "show_streak": True,
                "forward_streak_data": True,
                "forward_offer_nudge_data": False
            }
        }
    }


def create_single_config(campaign_name, campaign_type, duration_days, per_txn_reward):
    """
    Create single config (no suffix) for max_allowed = 1 campaigns.
    """
    # Campaign-type aware copy
    payment_text = "scan & pay" if campaign_type == "SNP" else "UPI payment"

    return {
        "config_key": campaign_name,
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
                "value": "UPI"  # Single txn campaigns use UPI type
            },
            "status": {
                "type": "STRING",
                "operator": "IN",
                "value": ["IN_PROGRESS", "ELIGIBLE"]
            }
        },
        "metadata": {
            "carousel": {
                "duration": 2000,
                "interval": 2000,
                "turns": 8,
                "timer_threshold": 172800000,
                "text": [
                    f"<format>assured <icon>INR</icon> {per_txn_reward} cashback on next {payment_text}</format>",
                    f"offer expires in {duration_days} days"
                ],
                "timer_prefix_asset": {}
            },
            "search": {
                "left_asset": {
                    "url": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/search_icon",
                    "type": "svg"
                },
                "text": "<format>search & pay contacts</format>",
                "border_animation_count": 2,
                "cta": {
                    "type": "p2p_home",
                    "additional_info": {
                        "search_phone_num_keyboard": True,
                        "headers": {},
                        "offer_nudge": {
                            "asset": {}
                        }
                    }
                },
                "right_asset": {
                    "asset": {}
                }
            },
            "config": {
                "show_streak": True,
                "forward_streak_data": True,
                "forward_offer_nudge_data": True
            },
            "cta": {}
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

    # Read original config
    with open(before_json_path, 'r') as f:
        data = json.load(f)

    # Unescape value
    value_str = data['value']
    value_unescaped = json.loads(value_str)

    # Find insertion index
    insertion_idx = find_insertion_index(value_unescaped['configs'])

    print(f"Processing SCAN_HOMEPAGE_CONFIG for: {campaign_name}")
    print(f"  Campaign type: {campaign_type}")
    print(f"  Duration: {duration_days} days")
    print(f"  Max allowed: {max_allowed}")
    print(f"  Insertion index: {insertion_idx}")

    # Create new configs based on max_allowed
    new_configs = []

    if max_allowed == 1:
        # Single transaction campaign
        print(f"  Creating single config: {campaign_name}")
        new_configs.append(create_single_config(campaign_name, campaign_type, duration_days, per_txn_reward))
    else:
        # Multi-transaction campaign
        print(f"  Creating 2 configs: {campaign_name}_0 and {campaign_name}_1_{max_allowed}")
        new_configs.append(create_initial_config(campaign_name, campaign_type, duration_days, total_offer, max_allowed))
        new_configs.append(create_inprogress_config(campaign_name, campaign_type, max_allowed, per_txn_reward))

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
    print(f"\n✓ SCAN_HOMEPAGE_CONFIG processing complete!")


if __name__ == "__main__":
    main()
