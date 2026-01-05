#!/usr/bin/env python3
"""
Process STREAK_ELIGIBILITY - Add new campaign
"""
import json
import sys

# Read the backup file (full GET response with all metadata)
with open(sys.argv[1], 'r') as f:
    full_response = json.load(f)

# Unescape the value field
value_unescaped = json.loads(full_response['value'])

# Campaign details from command line args
campaign_name = sys.argv[4]
campaign_type = sys.argv[5]
duration_days = int(sys.argv[6])
max_allowed = int(sys.argv[7])

# Build new campaign config
new_campaign = {
    "config_key": campaign_name,
    "uas_attributes": [
        {
            "attribute": {
                "namespace": "heimdall",
                "name": "heimdall.dynamic_attributes.streak_type"
            },
            "type": "STRING",
            "operator": "EQ",
            "value": campaign_name
        }
    ],
    "metadata": {
        "live": True,
        "streaks": [
            {
                "name": campaign_name,
                "type": campaign_type,
                "duration_in_days": duration_days,
                "max_allowed": max_allowed,
                "juno_check_enabled": True,
                "juno_percentage": 75,
                "same_day_unique_beneficiary_txn_allowed": True,
                "duplicate_beneficiary_txn_allowed": True,
                "self_transfer_allowed": False,
                "cross_beneficiary_name_check_enabled": False,
                "same_day_txn_allowed": True
            }
        ]
    }
}

# Add to configs array
value_unescaped['configs'].append(new_campaign)

# Save unescaped version for comparison
with open(sys.argv[2], 'w') as f:
    json.dump(value_unescaped, f, indent=2)

# Escape back for POST
full_response['value'] = json.dumps(value_unescaped, indent=2).replace('\n', '\r\n')

# Save the FULL response with ALL metadata fields for POST
with open(sys.argv[3], 'w') as f:
    json.dump(full_response, f, indent=2)

print("✓ Processed STREAK_ELIGIBILITY")
print(f"✓ Added campaign: {campaign_name}")
print(f"✓ Type: {campaign_type}, Duration: {duration_days} days, Max: {max_allowed}")
print(f"✓ Preserved metadata: created_by={full_response.get('created_by')}, updated_by={full_response.get('updated_by')}")
