#!/usr/bin/env python3
"""
Process STREAK_TXN_ELIGIBILITY - Add new campaign
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
min_amount = int(sys.argv[6])

# Determine flow_type based on campaign type
flow_type_map = {
    "UPI": ["SNP", "P2P"],
    "SNP": ["SNP"],
    "P2P": ["P2P"]
}
flow_type = flow_type_map.get(campaign_type, ["SNP", "P2P"])

# Build new campaign config
new_campaign = {
    "config_key": campaign_name,
    "conditions": {
        "streak_type": {
            "type": "STRING",
            "operator": "EQ",
            "value": campaign_type
        },
        "streak_name": {
            "type": "STRING",
            "operator": "EQ",
            "value": campaign_name
        },
        "flow_type": {
            "type": "STRING",
            "operator": "IN",
            "value": flow_type
        },
        "payment_type": {
            "type": "STRING",
            "operator": "EQ",
            "value": "DEBIT"
        },
        "amount": {
            "type": "NUMBER",
            "operator": "GTE",
            "value": min_amount
        }
    },
    "metadata": {
        "value": True
    }
}

value_unescaped['configs'].append(new_campaign)

# Save unescaped version for comparison
with open(sys.argv[2], 'w') as f:
    json.dump(value_unescaped, f, indent=2)

# Escape back for POST
full_response['value'] = json.dumps(value_unescaped, indent=2).replace('\n', '\r\n')

# Save the FULL response with ALL metadata fields for POST
with open(sys.argv[3], 'w') as f:
    json.dump(full_response, f, indent=2)

print("✓ Processed STREAK_TXN_ELIGIBILITY")
print(f"✓ Added campaign: {campaign_name}")
print(f"✓ Type: {campaign_type}, flow_type: {flow_type}, min_amount: {min_amount}")
print(f"✓ Preserved metadata: created_by={full_response.get('created_by')}, updated_by={full_response.get('updated_by')}")
