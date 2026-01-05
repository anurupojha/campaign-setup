# Campaign Setup System - Overview

## 🎯 The Magic Button

After 3 months away, you come back and run:

```bash
cd ~/Documents/campaign_setup
python3 setup_campaign_master.py
```

The system will:
- Ask you 12 questions about your campaign
- Automatically fetch 5-6 configs from the API
- Process all configs with correct patterns
- Generate complete session folder with all files
- Show you exactly what to review before posting

**Zero room for error. Zero manual work. Zero need to remember patterns.**

---

## What You Have

### The Master Script (`setup_campaign_master.py`)

This is your ONE entry point. It orchestrates everything:

1. **Input Collection** - Asks you all questions upfront:
   - Campaign name & ID
   - Type (UPI/SNP/P2P)
   - Duration & max allowed
   - Min transaction amount
   - RuPay? Bank-specific?
   - Total offer & banner
   - Bottom sheet copy
   - API credentials

2. **Config Determination** - Automatically knows which configs you need:
   - SNP campaigns → 5 configs
   - UPI/P2P campaigns → 6 configs

3. **Automatic Processing** - Calls all individual processors:
   - Fetches all configs via curl
   - Processes each with correct patterns
   - Handles escaping/unescaping
   - Inserts at correct positions
   - Applies all rules automatically

4. **Output Generation** - Creates complete session:
   - `<DATE>_<CAMPAIGN_NAME>/` folder
   - All `*_before.json` files
   - All `*_after_unescaped.json` (human-readable)
   - All `*_after.json` (ready to POST)
   - `campaign_info.txt` with summary & POST templates

5. **POST to Production (Optional)** - Asks for permission:
   - Two confirmations required
   - Posts all configs one by one
   - Verifies each config after posting
   - Saves `*_verify.json` files
   - Updates campaign_info.txt with status

### The Processing Scripts (`scripts/`)

Individual processors for each config type:

- `process_streak_eligibility.py` - Campaign eligibility rules
- `process_txn_eligibility.py` - Transaction-level rules
- `process_streak_config.py` - UI button text & colors
- `process_streak_block_template.py` - Banner & bottom sheet
- `process_scan_homepage_config.py` - SNP home screen carousel
- `process_ptp_streak_config.py` - P2P home screen carousel

**You never call these directly** - the master script calls them.

### The Documentation

- `README.md` - Quick start guide (points to master script)
- `campaign_setup_guide.md` - Complete technical reference (all 7 configs)
- `STREAK_BLOCK_TEMPLATE_banner_mapping.md` - Banner URL reference
- `SYSTEM_OVERVIEW.md` - This file (the big picture)

### The Session Backups (`backups/`)

Each campaign setup creates a folder:
```
backups/2026-01-02_upi_streak_5/
├── campaign_info.txt                         # Complete summary
├── STREAK_ELIGIBILITY_before.json            # Original from API
├── STREAK_ELIGIBILITY_after_unescaped.json   # Human-readable
├── STREAK_ELIGIBILITY_after.json             # Ready to POST (or already posted)
├── STREAK_ELIGIBILITY_verify.json            # Verification (if posted)
├── STREAK_TXN_ELIGIBILITY_before.json
├── STREAK_TXN_ELIGIBILITY_after_unescaped.json
├── STREAK_TXN_ELIGIBILITY_after.json
├── STREAK_TXN_ELIGIBILITY_verify.json
... (and so on for all configs)
```

---

## How It Works (Technical)

### Master Orchestration Flow

```
User runs script
    ↓
Collect 12 inputs upfront
    ↓
Determine configs needed (5 or 6 based on type)
    ↓
Create session folder with date + name
    ↓
For each config:
    - Fetch via GET curl
    - Save as *_before.json
    - Call processing script with correct params
    - Generate *_after_unescaped.json (readable)
    - Generate *_after.json (ready to POST)
    ↓
Generate campaign_info.txt with:
    - All campaign details
    - POST command templates
    - Next steps
    ↓
Show summary & file locations
    ↓
Ask: "POST to production now?" (TWO confirmations)
    ↓
If YES:
    - POST each config one by one
    - Verify each by fetching again
    - Save *_verify.json files
    - Update campaign_info.txt (status: LIVE)
    - Show success summary
    ↓
If NO:
    - Show review instructions
    - Files ready for manual POST later
```

### Key Design Patterns

1. **No Memory Required** - Script reads patterns from processed examples
2. **Type-Based Logic** - Automatically handles SNP vs UPI vs P2P differences
3. **Cascading Fallbacks** - Smart insertion logic for each config type
4. **Escape Handling** - Automatic JSON escaping with \r\n line endings
5. **Session Isolation** - Each campaign in its own dated folder
6. **Audit Trail** - Always keeps before/after for comparison
7. **Review Before POST** - Never posts automatically, always shows files first

### Config-Specific Intelligence

Each processor knows:
- **STREAK_ELIGIBILITY**: Always sets cross_beneficiary_name_check_enabled: false
- **STREAK_TXN_ELIGIBILITY**: Auto-determines flow_type from campaign type
- **STREAK_CONFIG**: Inserts before last config (fallback)
- **STREAK_BLOCK_TEMPLATE**: Handles Velocity template (not JSON)
- **SCAN_HOMEPAGE_CONFIG**: Creates _0 and _1_X with explicit suffixes, cascading insertion
- **PTP_STREAK_CONFIG**: Only for UPI/P2P, has streak_text in _0 config

---

## Supported Configs

| Config | SNP | UPI | P2P | Notes |
|--------|-----|-----|-----|-------|
| STREAK_ELIGIBILITY | ✓ | ✓ | ✓ | Always required |
| STREAK_TXN_ELIGIBILITY | ✓ | ✓ | ✓ | Always required |
| STREAK_CONFIG | ✓ | ✓ | ✓ | Always required |
| STREAK_BLOCK_TEMPLATE | ✓ | ✓ | ✓ | Always required |
| SCAN_HOMEPAGE_CONFIG | ✓ | ✓ | ✓ | Always required |
| PTP_STREAK_CONFIG | ✗ | ✓ | ✓ | Skip for SNP campaigns |
| EXPERIMENT_ID_LIST | ✗ | ✗ | ✗ | Not used, skip |

---

## Error-Proof Features

1. **Input Validation** - All inputs validated before processing
2. **Type Checking** - Campaign type determines which configs are processed
3. **File Existence Checks** - Verifies all required files exist
4. **API Error Handling** - Graceful failure with clear error messages
5. **Session Isolation** - Failed runs don't corrupt existing sessions
6. **Atomic Processing** - Each config processed independently
7. **Clear Output** - Color-coded terminal output shows progress
8. **Complete Logging** - All actions logged in campaign_info.txt
9. **Double Confirmation for POST** - Two "are you sure?" prompts before posting
10. **Automatic Verification** - Fetches configs after POST to confirm changes
11. **POST is Optional** - Can process without posting, review, then POST later

---

## The 3-Month Test

Scenario: You haven't touched this system in 3 months.

**What you do:**
```bash
cd ~/Documents/campaign_setup
python3 setup_campaign_master.py
```

**What happens:**
1. Script asks: "Campaign Name?" → You answer: "new_campaign_123"
2. Script asks: "Campaign ID?" → You answer: "abc-def-ghi"
3. Script asks: "Type?" → You answer: "2" (SNP)
4. Script asks 9 more questions → You answer them
5. Script says: "Processing..." → You wait 10 seconds
6. Script says: "✓ Complete! Review files in backups/2026-04-02_new_campaign_123/"
7. Script asks: "POST to production now?" → You choose:
   - **Option A**: Say "yes" → Script posts all configs, verifies them, campaign goes LIVE
   - **Option B**: Say "no" → Review files manually, POST later when ready
8. Done.

**What you DON'T need to remember:**
- Which configs are needed for SNP
- Where to insert in each config
- How flow_type is determined
- Suffix patterns (_0, _1_5, etc.)
- Escape sequences
- Insertion positions
- API endpoints
- curl syntax
- JSON structure
- Any patterns or rules

**The system remembers everything. You just answer questions.**

---

## Next Steps After Setup

### If You Chose to POST Automatically

**Already Done!** ✓
- All configs posted to production
- All changes verified
- Campaign is LIVE
- Verification files saved as `*_verify.json`
- campaign_info.txt updated with LIVE status

### If You Chose to Review First

1. **Review Files** - Check all `*_after.json` in session folder
2. **Compare Before/After** - Verify changes look correct
3. **POST to API** - Use templates in `campaign_info.txt`
4. **Verify** - Fetch configs again to confirm changes applied

POST command template (in campaign_info.txt):
```bash
curl -X POST \
  http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template \
  -H 'Content-Type: application/json' \
  -H 'userid: YOUR_USERID' \
  -H '_cred_apikey: YOUR_APIKEY' \
  -d @STREAK_ELIGIBILITY_after.json
```

---

## System Status

**Production Ready** ✓

- All 6 required configs automated
- Tested with real campaign (upi_streak_5)
- Error handling in place
- Documentation complete
- Session backup working
- Master script operational

**The magic is ready to unfold.**
