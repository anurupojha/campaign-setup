# Campaign Setup

Organized workspace for managing streak campaign configurations.

## 🚀 Quick Start

### Option 1: Enhanced UI (Recommended - Beautiful!)

```bash
cd ~/Documents/campaign_setup
python3 ui_enhanced.py
```

**Features:**
- ✨ Beautiful terminal interface with colors and progress bars
- 📋 Step-by-step wizard (7 simple steps)
- 🎨 Tables for banner/subtitle selection
- ✅ Live validation and smart defaults
- 📊 Summary preview before processing
- 🔒 Double confirmation before POST

### Option 2: Command Line

```bash
cd ~/Documents/campaign_setup
python3 setup_campaign_master.py
```

Both scripts do the same thing:
1. Ask you for all campaign details upfront
2. Determine which configs are needed based on campaign type
3. Fetch all configs from API automatically
4. Process all configs automatically
5. Generate complete summary and session files
6. Show you exactly what to review before posting

**The magic unfolds.**

## Structure

```
campaign_setup/
├── README.md                               # This file (you are here)
├── ui_enhanced.py                          # 🎯 ENHANCED UI (use this!)
├── setup_campaign_master.py                # 🎯 MASTER SCRIPT (command-line)
├── campaign_setup_guide.md                 # Complete technical documentation
├── STREAK_BLOCK_TEMPLATE_banner_mapping.md # Banner image reference
├── banner_registry.json                    # Banner callout database
├── subtitle_templates.json                 # Subtitle templates
├── credentials.json                        # API credentials (auto-created)
├── scripts/                                # Individual config processors
│   ├── process_streak_eligibility.py
│   ├── process_txn_eligibility.py
│   ├── process_streak_config.py
│   ├── process_streak_block_template.py
│   ├── process_scan_homepage_config.py
│   └── process_ptp_streak_config.py
└── backups/                                # Campaign session backups
    └── <DATE>_<CAMPAIGN_NAME>/            # One folder per campaign
        ├── campaign_info.txt               # Complete summary
        ├── *_before.json                   # Original configs
        ├── *_after_unescaped.json         # Human-readable versions
        └── *_after.json                    # Ready to POST

```

## How It Works

### Master Script (Recommended - Foolproof)

**Run once:**
```bash
python3 setup_campaign_master.py
```

**What happens:**
1. **Input Collection** - You answer questions about your campaign
2. **Config Determination** - Script figures out which configs you need:
   - SNP campaigns: 5 configs
   - UPI/P2P campaigns: 6 configs
3. **Automatic Fetching** - Gets all configs from API
4. **Automatic Processing** - Calls all processing scripts
5. **Summary Generation** - Creates campaign_info.txt with complete details
6. **Review** - All files ready to review
7. **POST to Production (Optional)** - You choose:
   - POST now → Script posts all configs automatically and verifies
   - Review first → Files ready for manual POST later

**Inputs you'll provide:**
- Campaign Name (e.g., upi_streak_5)
- Campaign ID (UUID)
- Type (UPI/SNP/P2P)
- Duration (days)
- Max Allowed (transactions)
- Min Transaction Amount
- RuPay campaign? (yes/no)
- Bank-specific? (yes/no, issuer code if yes)
- Total offer (e.g., Rs 50)
- Banner URL/filename
- Bottom sheet subtitle
- API credentials

**Output in `backups/<DATE>_<CAMPAIGN_NAME>/`:**
- All before/after JSON files for each config
- campaign_info.txt with POST command templates
- If you chose to POST: *_verify.json files confirming changes
- Ready to review, then POST (or already posted if you chose that option)

### Manual Process (For Granular Control)

1. **Read the Guide**: Open `campaign_setup_guide.md` for technical details
2. **Use Individual Scripts**: Process specific configs manually
3. **For Deep Dives**: When you need to understand exact patterns

## Files

- **setup_campaign_master.py** - 🎯 **THE MASTER SCRIPT** (your magic button)
- **campaign_setup_guide.md** - Complete technical documentation (all 7 configs)
- **STREAK_BLOCK_TEMPLATE_banner_mapping.md** - Banner URL reference
- **scripts/process_*.py** - Individual config processors (called by master)
- **backups/** - Session-based backups for audit trail

## Current Progress

**All configs documented and automated: ✓**

Configs supported:
- ✓ STREAK_ELIGIBILITY
- ✓ STREAK_TXN_ELIGIBILITY
- ✓ STREAK_CONFIG
- ✓ STREAK_BLOCK_TEMPLATE
- ✓ SCAN_HOMEPAGE_CONFIG
- ✓ PTP_STREAK_CONFIG
- ⊘ EXPERIMENT_ID_LIST (not used, skip)

System status: **Production Ready**
