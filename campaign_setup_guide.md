# Campaign Setup Guide

This document contains detailed specifications for setting up campaigns across all 7 config keys.

---

## 🎯 How to Use This System

### The Foolproof Way (Recommended)

**You don't need to read this entire guide to set up a campaign.**

Just run this one command:

```bash
cd ~/Documents/campaign_setup
python3 setup_campaign_master.py
```

The master script will:
1. Ask you for all campaign details upfront
2. Read this guide automatically to understand patterns
3. Determine which configs you need
4. Fetch and process everything automatically
5. Generate a complete summary for review

**Even after 3 months, just run that command. The magic unfolds.**

### When to Read This Guide

Read the detailed config sections below when you need to:
- Understand the technical patterns and rules
- Debug or modify a specific config
- Add support for new config types
- Train someone else on the system

### This Guide Contains

For each of the 7 configs, you'll find:
- **Purpose**: What this config controls
- **Structure Templates**: Exact JSON patterns to follow
- **Pattern Rules**: Critical naming and insertion logic
- **Required Inputs**: What information is needed
- **Common/Default Values**: Standard values across campaigns
- **Examples**: Real campaign walkthrough

---

## Safety Hygiene (ALWAYS FOLLOW)

**Before modifying any config:**

1. **Create Session Folder**: `~/Documents/campaign_setup/backups/<DATE>_<CAMPAIGN_NAME>/`
2. **Fetch & Backup**: Execute GET curl and save original response to `<CONFIG_KEY>_before.json`
3. **Modify**: Apply changes to the config (only modify `value` field)
4. **Save Modified**: Save modified version to `<CONFIG_KEY>_after.json`
5. **Compare**: Show diff between before and after
6. **User Review**: User confirms the changes look correct
7. **Post**: Only after confirmation, execute POST curl
8. **Verify**: Fetch again to confirm changes were applied correctly
9. **Save Campaign Info**: Create `campaign_info.txt` with campaign details

**Directory Structure:**
```
~/Documents/campaign_setup/
├── campaign_setup_guide.md                  # This guide
├── STREAK_BLOCK_TEMPLATE_banner_mapping.md  # Banner URL reference
├── scripts/
│   ├── process_streak_eligibility.py
│   ├── process_txn_eligibility.py
│   ├── process_streak_config.py
│   └── process_streak_block_template.py
└── backups/
    ├── 2026-01-02_upi_streak_5/
    │   ├── campaign_info.txt                # Campaign details
    │   ├── STREAK_ELIGIBILITY_before.json
    │   ├── STREAK_ELIGIBILITY_after.json
    │   ├── STREAK_TXN_ELIGIBILITY_before.json
    │   ├── STREAK_TXN_ELIGIBILITY_after.json
    │   ├── STREAK_CONFIG_before.json
    │   ├── STREAK_CONFIG_after.json
    │   ├── STREAK_BLOCK_TEMPLATE_before.json
    │   ├── STREAK_BLOCK_TEMPLATE_after.json
    │   ├── SCAN_HOMEPAGE_CONFIG_before.json
    │   ├── SCAN_HOMEPAGE_CONFIG_after.json
    │   ├── EXPERIMENT_ID_LIST_before.json
    │   ├── EXPERIMENT_ID_LIST_after.json
    │   ├── PTP_STREAK_CONFIG_before.json
    │   └── PTP_STREAK_CONFIG_after.json
    └── 2026-01-05_another_campaign/
        └── ...
```

**Why:**
- All campaign setup files in one organized location
- Processing scripts separated in scripts/ folder
- One backup folder per campaign setup session
- Clear "before" and "after" naming for audit trail
- All 7 configs grouped per campaign
- Easy to find: date + campaign name
- Easy to clean up old sessions (delete entire campaign folder)
- Guide and reference docs at top level

---

## 1. STREAK_ELIGIBILITY

### Purpose
Defines the eligibility criteria and rules for a streak campaign.

### What Gets Added
A new config entry is added to the `configs` array in the value field.

### Required User Inputs
1. **Campaign Name** (string) - e.g., `snp_flat_10_multilob_act_react_rupay_holders`
2. **Campaign Type** (enum: "UPI" | "SNP")
   - `UPI` = both p2p + scan & pay eligible
   - `SNP` = only scan & pay eligible
3. **Duration in Days** (number) - How many days the streak runs for
4. **Max Allowed** (number) - Maximum number of transactions allowed

### Pattern Rules
- **Consistent Naming**: The campaign name MUST appear in exactly 3 places:
  1. `config_key`
  2. `uas_attributes[0].value`
  3. `metadata.streaks[0].name`

### Structure Template
```json
{
  "config_key": "<CAMPAIGN_NAME>",
  "uas_attributes": [
    {
      "attribute": {
        "namespace": "heimdall",
        "name": "heimdall.dynamic_attributes.streak_type"
      },
      "type": "STRING",
      "operator": "EQ",
      "value": "<CAMPAIGN_NAME>"
    }
  ],
  "metadata": {
    "live": true,
    "streaks": [
      {
        "name": "<CAMPAIGN_NAME>",
        "type": "<CAMPAIGN_TYPE>",
        "duration_in_days": <DURATION>,
        "max_allowed": <MAX_ALLOWED>,
        "juno_check_enabled": true,
        "juno_percentage": 75,
        "same_day_unique_beneficiary_txn_allowed": true,
        "duplicate_beneficiary_txn_allowed": true,
        "self_transfer_allowed": false,
        "cross_beneficiary_name_check_enabled": false,
        "same_day_txn_allowed": true
      }
    ]
  }
}
```

### Common/Default Values
These values are typically consistent across campaigns:
- `uas_attributes[0].attribute.namespace`: `"heimdall"`
- `uas_attributes[0].attribute.name`: `"heimdall.dynamic_attributes.streak_type"`
- `uas_attributes[0].type`: `"STRING"`
- `uas_attributes[0].operator`: `"EQ"`
- `metadata.live`: `true`
- `metadata.streaks[0].juno_check_enabled`: `true`
- `metadata.streaks[0].juno_percentage`: `75`
- `metadata.streaks[0].same_day_unique_beneficiary_txn_allowed`: `true`
- `metadata.streaks[0].duplicate_beneficiary_txn_allowed`: `true`
- `metadata.streaks[0].self_transfer_allowed`: `false`
- `metadata.streaks[0].cross_beneficiary_name_check_enabled`: `false`
- `metadata.streaks[0].same_day_txn_allowed`: `true`

### Questions to Ask User
When user says "I want to set up campaign <name>", ask these 3 questions:
1. **Campaign Type**: UPI or SNP?
2. **Duration**: How many days?
3. **Max Allowed**: How many transactions?

(Note: Campaign ID will be collected but used in other configs, not STREAK_ELIGIBILITY)

### Example
Campaign: `snp_flat_10_multilob_act_react_rupay_holders`
- Type: UPI
- Duration: 1 day
- Max Allowed: 1 transaction

---

## 2. STREAK_TXN_ELIGIBILITY

### Purpose
Defines transaction-level eligibility rules for streak campaigns (which transactions count toward the streak).

### What Gets Added
A new config entry is added to the `configs` array in the value field.

### Required User Inputs
1. **Campaign Name** (automatically from STREAK_ELIGIBILITY)
2. **Campaign Type** (automatically from STREAK_ELIGIBILITY: UPI/SNP/P2P)
3. **Minimum Transaction Amount** (number) - Minimum amount for txn to be eligible
4. **Is RuPay Campaign?** (yes/no) - If yes, adds primary_instrument field
5. **Is Bank-Specific?** (yes/no) - If yes, ask for issuer_code

### Pattern Rules
- **Naming Consistency**: Campaign name appears in 2 places:
  1. `config_key`
  2. `conditions.streak_name.value`
- **Type Mapping**: `conditions.streak_type.value` matches `type` from STREAK_ELIGIBILITY
- **Flow Type Auto-determined** based on type from STREAK_ELIGIBILITY:
  - If type = "UPI" → flow_type = `["SNP", "P2P"]`
  - If type = "SNP" → flow_type = `["SNP"]`
  - If type = "P2P" → flow_type = `["P2P"]`

### Structure Template
```json
{
  "config_key": "<CAMPAIGN_NAME>",
  "conditions": {
    "streak_type": {
      "type": "STRING",
      "operator": "EQ",
      "value": "<TYPE_FROM_ELIGIBILITY>"
    },
    "streak_name": {
      "type": "STRING",
      "operator": "EQ",
      "value": "<CAMPAIGN_NAME>"
    },
    "flow_type": {
      "type": "STRING",
      "operator": "IN",
      "value": <FLOW_TYPE_ARRAY>
    },
    "payment_type": {
      "type": "STRING",
      "operator": "EQ",
      "value": "DEBIT"
    },
    "amount": {
      "type": "NUMBER",
      "operator": "GTE",
      "value": <MIN_AMOUNT>
    }
  },
  "metadata": {
    "value": true
  }
}
```

### Optional Fields (Campaign-Specific)

**For RuPay Campaigns** - Add this field to conditions:
```json
"primary_instrument": {
  "type": "STRING",
  "operator": "IN",
  "value": ["UPI_CC"]
}
```

**For Bank-Specific Campaigns** - Add this field to conditions:
```json
"issuer_code": {
  "type": "STRING",
  "operator": "EQ",
  "value": "<BANK_ISSUER_CODE>"
}
```

### Common/Default Values
- `conditions.streak_type.operator`: `"EQ"`
- `conditions.streak_name.operator`: `"EQ"`
- `conditions.flow_type.operator`: `"IN"`
- `conditions.payment_type`: Always `"DEBIT"`
- `conditions.amount.operator`: `"GTE"`
- `metadata.value`: Always `true`

### Questions to Ask User
When setting up STREAK_TXN_ELIGIBILITY for a campaign:
1. Is this a RuPay campaign? (yes/no)
2. Is this bank-specific? If yes, what is the bank issuer code?
3. What is the minimum transaction amount for eligibility?

(Type and flow_type are auto-determined from STREAK_ELIGIBILITY)

### Example
Campaign: `upi_streak_5`
- Type from ELIGIBILITY: SNP
- streak_type: "SNP"
- flow_type: ["SNP"]
- Min amount: 10
- Not RuPay, not bank-specific

**Complete config:**
```json
{
  "config_key": "upi_streak_5",
  "conditions": {
    "streak_type": {
      "type": "STRING",
      "operator": "EQ",
      "value": "SNP"
    },
    "streak_name": {
      "type": "STRING",
      "operator": "EQ",
      "value": "upi_streak_5"
    },
    "flow_type": {
      "type": "STRING",
      "operator": "IN",
      "value": ["SNP"]
    },
    "payment_type": {
      "type": "STRING",
      "operator": "EQ",
      "value": "DEBIT"
    },
    "amount": {
      "type": "NUMBER",
      "operator": "GTE",
      "value": 10
    }
  },
  "metadata": {
    "value": true
  }
}
```

---

## 3. STREAK_CONFIG

### Purpose
Defines UI display configuration for streak campaigns (button text, colors).

### What Gets Added
A new config entry is added to the `configs` array BEFORE the last entry (fallback config).

### Required User Inputs
1. **Campaign ID (UUID)** (collected upfront)

### Pattern Rules
- **Campaign ID Only**: Uses campaign_id (UUID), not campaign name
- **Insertion Position**: MUST be inserted BEFORE the last config (empty conditions fallback)
- **Fallback Config**: The last config always has empty conditions `{}` and serves as default
- **Newer Campaigns**: Use `show_actual_reward_text: true`

### Structure Template
```json
{
  "conditions": {
    "campaign_id": {
      "type": "STRING",
      "value": "<CAMPAIGN_UUID>",
      "operator": "EQ"
    }
  },
  "metadata": {
    "claimed_state_text": "",
    "allotted_state_text": "<format><text fgClr='#B3FFEB34'>CLAIM</text></format>",
    "next_state_text": "",
    "default_state_text": "",
    "show_actual_reward_text": true
  }
}
```

### Common/Default Values
- `conditions.campaign_id.type`: `"STRING"`
- `conditions.campaign_id.operator`: `"EQ"`
- `metadata.claimed_state_text`: `""` (empty)
- `metadata.allotted_state_text`: `"<format><text fgClr='#B3FFEB34'>CLAIM</text></format>"`
- `metadata.next_state_text`: `""` (empty)
- `metadata.default_state_text`: `""` (empty)
- `metadata.show_actual_reward_text`: `true` (for newer campaigns)

### Questions to Ask User
No additional questions needed - uses campaign_id from initial setup.

### Important Notes
- **CRITICAL**: Always insert BEFORE the last config (empty conditions)
- The last config with `conditions: {}` is a fallback and must remain last
- All text fields remain empty except `allotted_state_text`
- Color `#B3FFEB34` is standard across all campaigns

### Example
Campaign: `upi_streak_5`
- Campaign ID: abcd123456
- Inserted at position 27 (before fallback at position 28)

**Complete config:**
```json
{
  "conditions": {
    "campaign_id": {
      "type": "STRING",
      "value": "abcd123456",
      "operator": "EQ"
    }
  },
  "metadata": {
    "claimed_state_text": "",
    "allotted_state_text": "<format><text fgClr='#B3FFEB34'>CLAIM</text></format>",
    "next_state_text": "",
    "default_state_text": "",
    "show_actual_reward_text": true
  }
}
```

---

## 4. STREAK_BLOCK_TEMPLATE

### Purpose
Defines UI display configuration for streak bottom sheets (banner images and per-transaction reward text).

### What Gets Added
Two additions to a Velocity template (NOT a JSON configs array):
1. Campaign ID added to banner asset URL condition
2. New #elseif block for bottom_sheet reward text

### Required User Inputs
1. **Banner Image:** What banner matches the total campaign offer?
   - If banner exists → Reuse and add campaign to condition
   - If new banner needed → User provides URL
2. **Bottom Sheet Title:** Per-transaction reward text (e.g., "earn Rs 10")
3. **Bottom Sheet Subtitle:** Action text (e.g., "make a QR payment to any merchant and claim cashback")

### Key Pattern Rules
**CRITICAL CONCEPT:**
- **Banner Image = TOTAL offer** (e.g., "Rs 50 on 5 payments")
- **Bottom Sheet Text = PER-TRANSACTION reward** (e.g., "earn Rs 10" = 50÷5)

**Uniqueness:**
- ✓ Each campaign has its own unique bottom_sheet block
- ✓ Multiple campaigns can share the same banner image

### Structure Overview

**This is a Velocity Template**, not JSON. It uses:
- `#if`, `#elseif`, `#else`, `#end` directives
- Template variables: `$!campaign_id`, `$!streak_type`, etc.
- Conditional logic based on campaign_id

**Two main sections:**

#### Section 1: Banner Asset URL (`banner_data.asset.url`)
```velocity
#elseif($!campaign_id == "xxx" || $!campaign_id == "yyy" || $!campaign_id == "abcd123456")
"url": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/snp_streak_bottomsheet.png",
```

#### Section 2: Bottom Sheet Text (`streak_data[].bottom_sheet.reward_details`)
```velocity
#elseif($!campaign_id == "abcd123456")
    #if($streak_item.status != "allotted" && $streak_item.status != "claimed")
    ,
    "bottom_sheet": {
        "reward_details": {
            "title": "<format>earn <icon>INR</icon>10</format>",
            "subtitle": "make a QR payment to \\nany merchant and claim cashback"
        }
    }
    #end
```

### Standard Banner URLs

| Banner File | Visual Description | Typical Use Case |
|------------|-------------------|------------------|
| `snp_streak_bottomsheet.png` | Purple/Yellow cash, User icon, QR | SNP campaigns (default) |
| `upi_streak_bottomsheet.png` | Purple/Yellow cash, User icon, QR | UPI campaigns |
| `p2p_streak_bottomsheet.png` | Purple/Yellow cash, User icon, QR | P2P campaigns |
| `rupay_streak_3.png` | RuPay card + UPI logo + QR stand | RuPay campaigns |

**Default Fallback:** `snp_streak_bottomsheet.png`

### Bottom Sheet Text Patterns

**Pattern 1 - SNP/QR Focus:**
```
"title": "<format>earn <icon>INR</icon>10</format>",
"subtitle": "make a QR payment to \\nany merchant and claim cashback"
```

**Pattern 2 - Assured Cashback:**
```
"title": "<format>earn <icon>INR</icon>10 cashback</format>",
"subtitle": "<format>make a UPI payment to claim assured <icon>INR</icon>10 cashback</format>"
```

**Pattern 3 - UPI Broader:**
```
"title": "<format>earn <icon>INR</icon>20</format>",
"subtitle": "make a UPI payment to any merchant\\nor contact and claim cashback"
```

Note: `\\n` creates a line break in the UI

### Questions to Ask User

When setting up STREAK_BLOCK_TEMPLATE for a campaign:

1. **What is the total campaign offer?** (e.g., "Rs 50 on 5 payments")
2. **Does a banner exist for this offer?** Check banner images
   - If yes → Which banner URL?
   - If no → User will provide new banner URL
3. **What is the per-transaction reward?** (Calculate: Total ÷ Number of transactions)
4. **What should the bottom_sheet subtitle be?** (Always ask, don't assume)

### Example

Campaign: `upi_streak_5`
- Total Offer: Rs 50 on 5 payments
- Per-Transaction: Rs 10 (50 ÷ 5 = 10)
- Campaign Type: SNP

**Banner:**
- Matches existing: `snp_streak_bottomsheet.png`
- Shows: "Rs 50 cashback on 5 payments"

**Bottom Sheet:**
- Title: `<format>earn <icon>INR</icon>10</format>`
- Subtitle: `make a QR payment to \\nany merchant and claim cashback`

**Changes made:**
1. Added `|| $!campaign_id == "abcd123456"` to snp_streak_bottomsheet.png condition
2. Added new #elseif block with per-transaction reward text

### Important Notes
- This is a **Velocity Template**, not JSON - modify as a string
- **Always ask for bottom_sheet subtitle** - don't assume based on campaign type
- **Both sections have #else as the LAST block** (default fallback)
- Insert bottom_sheet block BEFORE the `#else` (default fallback)
- **Banner URLs: Two cases to handle:**
  - **Case A:** Banner URL exists → Add campaign to existing condition with `||`
  - **Case B:** Banner URL is new → Add new `#elseif` block BEFORE `#else`
- Banner images show total offer, bottom sheet shows per-transaction reward
- Line breaks in subtitle use `\\n` (escaped backslash-n)
- **Created internal mapping:** See `STREAK_BLOCK_TEMPLATE_banner_mapping.md` for URL→Offer reference

---

## 5. SCAN_HOMEPAGE_CONFIG

### Purpose
Controls the carousel and search UI on the **Scan (SNP) home screen**. Shows campaign offers to users.

### When to Use
- ✓ **ALL campaign types**: SNP, UPI, P2P
- This config is always needed for all streak campaigns

### What Gets Added
- **For multi-transaction campaigns** (max_allowed ≥ 2): TWO configs added
  - `<campaign_name>_0`: Initial state (no transactions yet)
  - `<campaign_name>_1_X`: In-progress state (1+ transactions completed)
- **For single-transaction campaigns** (max_allowed = 1): ONE config added
  - `<campaign_name>`: No suffix

### Required User Inputs
1. **Campaign Name** (from STREAK_ELIGIBILITY)
2. **Campaign Type** (from STREAK_ELIGIBILITY: SNP/UPI/P2P)
3. **Duration Days** (from STREAK_ELIGIBILITY)
4. **Max Allowed** (from STREAK_ELIGIBILITY)
5. **Per-Transaction Reward** (total_offer ÷ max_allowed)
6. **Total Offer** (e.g., 50 if "Rs 50 on 5 payments")

### Pattern Rules
- **Suffix naming** (explicit based on max_allowed):
  - max_allowed = 1 → No suffix
  - max_allowed = 3 → `_0` and `_1_3`
  - max_allowed = 4 → `_0` and `_1_4`
  - max_allowed = 5 → `_0` and `_1_5`
  - max_allowed = 7 → `_0` and `_1_7`
  - Pattern: `_1_X` where X = max_allowed
- **Insertion point**: BEFORE first system config (cascading fallbacks):
  1. Try: `widget_assured_20_and`
  2. Fallback: `widget_assured_20_ios`
  3. Fallback: `widget_campaign_and`
  4. Fallback: `widget_campaign_ios`
  5. Fallback: `wr_pay_ios`
  6. Fallback: `wr_pay_android`
  7. Fallback: `snp_catch_all`
- **NO viewport field** for standard campaigns (only for special partnerships)
- **NO segments field** unless explicitly specified

### Structure Template (_0 config - Initial State)
```json
{
  "config_key": "<campaign_name>_0",
  "uas_attributes": [
    {
      "attribute": {
        "namespace": "heimdall",
        "name": "heimdall.dynamic_attributes.streak_type"
      },
      "type": "STRING",
      "operator": "IN",
      "value": ["<campaign_name>"]
    }
  ],
  "conditions": {
    "type": {
      "type": "STRING",
      "operator": "EQ",
      "value": "<campaign_type>"
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
        "<format>assured cashback of <icon>INR</icon><total> on next <max> payments</format>",
        "offer expires in <duration> days"
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
          "search_phone_num_keyboard": true,
          "headers": {},
          "offer_nudge": {"asset": {}}
        }
      },
      "right_asset": {"asset": {}}
    },
    "config": {
      "show_streak": true,
      "forward_streak_data": true,
      "forward_offer_nudge_data": true
    },
    "cta": {}
  }
}
```

### Structure Template (_1_X config - In-Progress State)
```json
{
  "config_key": "<campaign_name>_1_<max_allowed>",
  "uas_attributes": [/* same as _0 */],
  "conditions": {
    "type": {
      "type": "STRING",
      "operator": "EQ",
      "value": "<campaign_type>"
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
      "offer_text": "<format>assured <icon>INR</icon><per_txn> cashback on next QR payment</format>"
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
          "search_phone_num_keyboard": true
        }
      }
    },
    "config": {
      "show_streak": true,
      "forward_streak_data": true,
      "forward_offer_nudge_data": false
    }
  }
}
```

### Key Differences Between _0 and _1_X

| Field | _0 (Initial) | _1_X (In-Progress) |
|-------|--------------|-------------------|
| **completed condition** | NOT present | `>= 1` |
| **carousel.text** | Array with 2 lines | NOT present |
| **carousel.offer_text** | NOT present | Single string |
| **carousel.streak_text** | NOT present | "ends in <expiry_timer>" |
| **search.right_asset** | Empty object | `{"text": "CASHBACK"}` |
| **forward_offer_nudge_data** | `true` | `false` |

### Questions to Ask User
No additional questions - all inputs come from previous configs.

### Example
Campaign: `upi_streak_5`
- Type: SNP
- Duration: 14 days
- Max Allowed: 5
- Total Offer: 50
- Per-Transaction: 10

Creates:
- `upi_streak_5_0`: "assured cashback of ₹50 on next 5 payments" + "offer expires in 14 days"
- `upi_streak_5_1_5`: "assured ₹10 cashback on next QR payment"

---

## 6. EXPERIMENT_ID_LIST

### Purpose
Used for A/B testing experiment assignments.

### When to Use
**NOT USED** - Skip this config entirely for standard campaign setup.

### Notes
This config is maintained by the experimentation team and is not part of standard campaign setup workflow.

---

## 7. PTP_STREAK_CONFIG

### Purpose
Controls the carousel and search UI on the **P2P (peer-to-peer) home screen**.

### When to Use
- ✓ **UPI campaigns** (type: "UPI") - Shows on P2P home since UPI includes P2P
- ✓ **P2P campaigns** (type: "P2P") - Shows on P2P home
- ✗ **SNP campaigns** (type: "SNP") - SKIP this config (SNP doesn't appear on P2P home)

### What Gets Added
**For UPI/P2P campaigns**: TWO configs added
- `<campaign_name>_0`: Initial state (no transactions yet)
- `<campaign_name>_1_X`: In-progress state (1+ transactions completed)

Note: Single-transaction pattern not applicable (P2P campaigns are typically multi-transaction)

### Required User Inputs
Same as SCAN_HOMEPAGE_CONFIG - all inputs come from previous configs.

### Pattern Rules
- **Same suffix pattern** as SCAN_HOMEPAGE_CONFIG (`_1_X` where X = max_allowed)
- **Insertion point**: BEFORE `p2p_default` (fallback config)
  - Fallback: `p2p_0_state` if p2p_default not found
- **Type must be UPI or P2P** - script will error if type is SNP

### Key Differences from SCAN_HOMEPAGE_CONFIG

| Field | SCAN_HOMEPAGE_CONFIG | PTP_STREAK_CONFIG |
|-------|---------------------|-------------------|
| **_0 streak_text** | NOT present | `"ENDS IN <expiry_timer>"` |
| **search structure** | `left_asset`, `text`, `border_animation_count` | `data` array with 7 pay icons |
| **cta field** | Empty object `{}` | Deeplink to scan_pay |
| **search.interval** | Not present | `1000` |
| **search.turns** | Not present | `15` |

### Structure Template (_0 config - Initial State)
```json
{
  "config_key": "<campaign_name>_0",
  "uas_attributes": [/* same structure as SCAN_HOMEPAGE_CONFIG */],
  "conditions": {
    "type": {
      "type": "STRING",
      "operator": "EQ",
      "value": "<campaign_type>"
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
        "<format>assured <icon>INR</icon><total> cashback on <max> UPI payments</format>",
        "<format>offer expires in <duration> days</format>"
      ]
    },
    "search": {
      "data": [
        /* 7 standard pay option items with icons */
      ],
      "interval": 1000,
      "turns": 15
    },
    "config": {
      "show_streak": true,
      "forward_streak_data": true,
      "forward_offer_nudge_data": true
    }
  }
}
```

### Structure Template (_1_X config - In-Progress State)
Similar to _0 but:
- Has `completed >= 1` condition
- Uses `offer_text` instead of `text` array
- Same `streak_text: "ENDS IN <expiry_timer>"`

### Example
Campaign: `upi_test_campaign` (type: UPI)
- Duration: 14 days
- Max Allowed: 5
- Total: 50, Per-transaction: 10

Creates:
- `upi_test_campaign_0`: Has both `text` array AND `streak_text`
- `upi_test_campaign_1_5`: Has `offer_text` AND `streak_text`

### Questions to Ask User
No additional questions - determined by campaign type from STREAK_ELIGIBILITY.

### Important Notes
- **Script validates type**: Will error if type is "SNP"
- **_0 config has BOTH** text array AND streak_text (unlike SCAN_HOMEPAGE_CONFIG)
- **Standard search.data array** is hardcoded (7 pay icons with contacts/phone options)
- Skip this config entirely for SNP campaigns

---

## API Endpoints Structure

**GET Request:**
- URL: `http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template/<CONFIG_KEY>`
- Example: `.../template/STREAK_ELIGIBILITY`
- Headers: `userid`, `_cred_apikey`

**POST Request:**
- URL: `http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template` (base URL, NO config key suffix)
- Headers: `userid`, `_cred_apikey`, `Content-Type: application/json`
- Body: ENTIRE object from GET response with modified `value` field

**POST Body Structure:**
```json
{
  "key": "STREAK_ELIGIBILITY",
  "description": "Check whether a user is eligible for streak",
  "value": "<escaped JSON here>",
  "created_by": "...",
  "updated_by": "...",
  "schema": "...",
  "is_simple_config": false
}
```

**IMPORTANT:**
- **ONLY modify the `value` field** - all other fields remain unchanged
- Preserve: `key`, `description`, `created_by`, `updated_by`, `schema`, `is_simple_config`
- URL changes: GET uses `.../template/<KEY>`, POST uses `.../template`
- The API will handle `updated_by` automatically - do not modify it

---

## Notes
- Campaign ID (UUID) is not used in STREAK_ELIGIBILITY but will be used in other configs
- All modifications happen within the "value" field's "configs" array
- JSON in the API is escaped (with \r\n line endings)
- POST must include all metadata fields from GET response
- **Each of the 7 configs has a different structure** - we'll document each as we progress
- All 7 configs follow the same API pattern: GET from `.../template/<KEY>`, POST to `.../template`
