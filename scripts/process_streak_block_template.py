#!/usr/bin/env python3
"""
Process STREAK_BLOCK_TEMPLATE - Add campaign to Velocity template
This is a VELOCITY TEMPLATE, not JSON. We modify it as a string.
"""
import json
import sys
import re

# Read the backup file (full GET response with all metadata)
with open(sys.argv[1], 'r') as f:
    full_response = json.load(f)

# The value field is already a string containing a Velocity template with \r\n
# We just work with it as a string (it's not JSON, it's Velocity template syntax)
template = full_response['value']

# Campaign details from command line
campaign_id = sys.argv[4]
banner_url = sys.argv[5]
bottom_sheet_title = sys.argv[6]
bottom_sheet_subtitle = sys.argv[7]

print(f"Processing STREAK_BLOCK_TEMPLATE for campaign: {campaign_id}")
print(f"Banner URL: {banner_url}")
print(f"Bottom Sheet Title: {bottom_sheet_title}")
print(f"Bottom Sheet Subtitle: {bottom_sheet_subtitle}")
print()

# ===========================================================================
# MODIFICATION 1: Add campaign_id to banner asset URL condition
# ===========================================================================

# Two cases:
# Case A: Banner URL EXISTS → Add campaign to existing condition
# Case B: Banner URL is NEW → Add new #elseif block BEFORE #else

banner_pattern = re.escape(banner_url)
banner_condition_pattern = rf'(#elseif\([^)]*\))\s*"url":\s*"{banner_pattern}"'

match = re.search(banner_condition_pattern, template)
if match:
    # Case A: Banner URL exists, add to existing condition
    old_condition = match.group(1)

    # Check if our campaign is already in the condition
    if f'$!campaign_id == "{campaign_id}"' in old_condition:
        print(f"⚠ WARNING: Campaign {campaign_id} already exists in banner condition!")
        print(f"  Skipping banner modification to avoid duplicate.")
    else:
        # Add our campaign to the condition with ||
        new_condition = old_condition.rstrip(')') + f' || $!campaign_id == "{campaign_id}")'
        template = template.replace(old_condition, new_condition, 1)
        print(f"✓ Case A: Added campaign to existing banner condition")
        print(f"  Old: {old_condition}")
        print(f"  New: {new_condition}")
        print(f"  ⚠ Note: This banner URL is shared with other campaigns")
else:
    # Case B: Banner URL is new, add new #elseif block BEFORE #else
    print(f"✓ Case B: Banner URL is NEW, adding new condition block")

    # Find the #else block in banner section (before "type": "image")
    banner_else_pattern = r'(#elseif\(\$!campaign_id[^#]+)\s+(#else\s+"url":)'
    banner_match = re.search(banner_else_pattern, template)

    if banner_match:
        # Insert new #elseif block before #else
        new_banner_block = f'''              #elseif($!campaign_id == "{campaign_id}")
              "url": "{banner_url}",
              '''

        insertion_point = banner_match.start(2)
        template = template[:insertion_point] + new_banner_block + template[insertion_point:]
        print(f"  Added new banner condition for campaign {campaign_id}")
        print(f"  URL: {banner_url}")
    else:
        print(f"✗ ERROR: Could not find insertion point for new banner URL")
        sys.exit(1)

print()

# ===========================================================================
# MODIFICATION 2: Add bottom_sheet block for this campaign
# ===========================================================================

# We need to add a new #elseif block in the bottom_sheet section
# Find a good insertion point - after the last campaign-specific block, before #else

# Build the new bottom_sheet block
new_bottom_sheet_block = f'''          #elseif($!campaign_id == "{campaign_id}")
              #if($streak_item.status != "allotted" && $streak_item.status != "claimed")
              ,
          "bottom_sheet": {{
              "reward_details": {{
                  "title": "{bottom_sheet_title}",
                  "subtitle": "{bottom_sheet_subtitle}"
              }}
          }}
              #end'''

# Find the #else block at the end (default fallback for bottom_sheet)
# Insert our new block BEFORE the #else
# Look for the last #end followed by whitespace before #else
default_bottom_sheet_pattern = r'(#end\s+)(#else\s+#if\(\$streak_item\.status)'

match = re.search(default_bottom_sheet_pattern, template)
if match:
    # Insert between the #end and #else
    insertion_point = match.start(2)
    template = template[:insertion_point] + new_bottom_sheet_block + '\r\n          ' + template[insertion_point:]
    print(f"✓ Added bottom_sheet block for campaign {campaign_id}")
    print(f"  Title: {bottom_sheet_title}")
    print(f"  Subtitle: {bottom_sheet_subtitle}")
else:
    print(f"✗ ERROR: Could not find insertion point for bottom_sheet block")
    sys.exit(1)

print()

# ===========================================================================
# Save the modified template
# ===========================================================================

# Save unescaped version for comparison (as .txt since it's a Velocity template)
# The template already has \r\n, so we need to unescape for viewing
unescaped_template = template.replace('\\r\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
with open(sys.argv[2], 'w') as f:
    f.write(unescaped_template)

# The template string already has proper escaping (\r\n), just update the value field
full_response['value'] = template

# Save the FULL response with ALL metadata fields for POST
with open(sys.argv[3], 'w') as f:
    json.dump(full_response, f, indent=2)

print("✓ Processed STREAK_BLOCK_TEMPLATE")
print(f"✓ Added campaign_id: {campaign_id}")
print(f"✓ Banner: Added to condition block")
print(f"✓ Bottom Sheet: Added unique block")
print(f"✓ Preserved metadata: created_by={full_response.get('created_by')}, updated_by={full_response.get('updated_by')}")
