#!/usr/bin/env python3
"""
Process STREAK_CONFIG - Add new campaign before the fallback config
"""
import json
import sys

# Read the backup file (full GET response with all metadata)
with open(sys.argv[1], 'r') as f:
    full_response = json.load(f)

# Unescape the value field
value_unescaped = json.loads(full_response['value'])

# Campaign details from command line args
campaign_id = sys.argv[4]

# Build new campaign config
new_campaign = {
    "conditions": {
        "campaign_id": {
            "type": "STRING",
            "value": campaign_id,
            "operator": "EQ"
        }
    },
    "metadata": {
        "claimed_state_text": "",
        "allotted_state_text": "<format><text fgClr='#B3FFEB34'>CLAIM</text></format>",
        "next_state_text": "",
        "default_state_text": "",
        "show_actual_reward_text": True
    }
}

# IMPORTANT: Insert BEFORE the last config (empty conditions fallback)
# The last config should always remain at the end
value_unescaped['configs'].insert(-1, new_campaign)

# Save unescaped version for comparison
with open(sys.argv[2], 'w') as f:
    json.dump(value_unescaped, f, indent=2)

# Escape back for POST
full_response['value'] = json.dumps(value_unescaped, indent=2).replace('\n', '\r\n')

# Save the FULL response with ALL metadata fields for POST
with open(sys.argv[3], 'w') as f:
    json.dump(full_response, f, indent=2)

print("✓ Processed STREAK_CONFIG")
print(f"✓ Added campaign_id: {campaign_id}")
print(f"✓ Inserted before fallback config (empty conditions)")
print(f"✓ show_actual_reward_text: true (newer campaign pattern)")
print(f"✓ Preserved metadata: created_by={full_response.get('created_by')}, updated_by={full_response.get('updated_by')}")
