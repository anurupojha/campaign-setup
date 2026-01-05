# Enhanced UI Usage Guide

## What It Looks Like

When you run `python3 ui_enhanced.py`, you'll see:

### Step 1: Header
```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              Campaign Setup Wizard                       ║
║     Simplified campaign configuration for streak         ║
║                    campaigns                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Step 2: Basic Details (Step 1/7)
```
╭──────────────────────────────────────────────────────────╮
│ Step 1/7: Basic Campaign Details                        │
╰──────────────────────────────────────────────────────────╯

Campaign Name (e.g., upi_streak_6): upi_streak_7
✓ Campaign: upi_streak_7

Campaign ID is provided by your team
Campaign ID (UUID from team): 3f7a8b2c-9d1e-4f6a-b8c3-5e2d7f9a1b4c
✓ Campaign ID: 3f7a8b2c-9d1e-4f6a-b8c3-5e2d7f9a1b4c

Campaign Type:
[1]  UPI  - Both P2P + Scan & Pay eligible
[2]  SNP  - Scan & Pay only
[3]  P2P  - Peer-to-peer only
Select type [1/2/3]: 1
✓ Type: UPI

Duration (days) [14]: 14
Max Allowed (transactions) [5]: 5
✓ Duration: 14 days
✓ Max Transactions: 5
```

### Step 3: Transaction Details (Step 2/7)
```
╭──────────────────────────────────────────────────────────╮
│ Step 2/7: Transaction Details                           │
╰──────────────────────────────────────────────────────────╯

Minimum Transaction Amount (Rs) [10]: 10
Total Campaign Offer (Rs) (for 5 payments) [50]: 50

✓ Min Transaction: Rs 10
✓ Total Offer: Rs 50
✓ Per-Transaction: Rs 10 (auto-calculated)
```

### Step 4: Eligibility (Step 3/7)
```
╭──────────────────────────────────────────────────────────╮
│ Step 3/7: Additional Eligibility                        │
╰──────────────────────────────────────────────────────────╯

Is this a RuPay campaign? [y/N]: n
Is this bank-specific? [y/N]: n

✓ RuPay: No
✓ Bank-Specific: No
```

### Step 5: Banner Selection (Step 4/7)
```
╭──────────────────────────────────────────────────────────╮
│ Step 4/7: Banner Selection                              │
╰──────────────────────────────────────────────────────────╯

        Available Banners
╭──────┬────────────────────────────────────────╮
│  ID  │ Callout                                │
├──────┼────────────────────────────────────────┤
│  [1] │ Rs 10 cashback on next payment         │
│  [2] │ Rs 25 cashback on next payment         │
│  [3] │ Rs 30 cashback on next payment         │
│  [4] │ Rs 50 cashback on next payment         │
│  [5] │ upto Rs 50 cashback on next payment    │
│  [6] │ Rs 30 cashback on 3 payments           │
│  [7] │ Rs 60 cashback on 3 payments           │
│  [8] │ Rs 50 cashback on 5 payments           │
│  [9] │ Rs 75 cashback on 5 payments           │
│ [10] │ Rs 100 cashback on 5 payments          │
│ [11] │ Rs 125 cashback on 5 payments          │
│  [0] │ Enter custom banner                    │
╰──────┴────────────────────────────────────────╯

Select banner (Suggestion: look for 'Rs 50 on 5 payments'): 8
✓ Selected: Rs 50 cashback on 5 payments
```

### Step 6: Subtitle Selection (Step 5/7)
```
╭──────────────────────────────────────────────────────────╮
│ Step 5/7: Bottom Sheet Subtitle                         │
╰──────────────────────────────────────────────────────────╯

      Available Subtitles
╭──────┬──────────────────────────────────────────╮
│  ID  │ Text                                     │
├──────┼──────────────────────────────────────────┤
│  [1] │ make a QR payment to \nany merchant...   │
│  [2] │ make a UPI payment to any merchant...    │
│  [3] │ make a UPI payment to claim assured...   │
│  [0] │ Enter custom subtitle                    │
╰──────┴──────────────────────────────────────────╯

Select subtitle: 1
✓ Selected: make a QR payment to \nany merchant and claim cashback
```

### Step 7: Summary (Step 6/7)
```
╭──────────────────────────────────────────────────────────╮
│ Step 6/7: Campaign Summary                              │
╰──────────────────────────────────────────────────────────╯

╔═══════════════════════════╤═══════════════════════════════╗
║ Campaign Name             │ upi_streak_7                  ║
║ Campaign ID               │ 3f7a8b2c-9d1e-4f6a-b8c3...    ║
║ Type                      │ UPI                           ║
║ Duration                  │ 14 days                       ║
║ Max Transactions          │ 5                             ║
║ Total Offer               │ Rs 50                         ║
║ Per-Transaction Reward    │ Rs 10                         ║
║ Min Transaction Amount    │ Rs 10                         ║
║ RuPay Campaign            │ No                            ║
║ Bank-Specific             │ No                            ║
║ Banner                    │ snp_streak_bottomsheet.png    ║
║ Bottom Sheet              │ make a QR payment to...       ║
╚═══════════════════════════╧═══════════════════════════════╝

Configs to be processed: 6
  1. STREAK_ELIGIBILITY
  2. STREAK_TXN_ELIGIBILITY
  3. STREAK_CONFIG
  4. STREAK_BLOCK_TEMPLATE
  5. SCAN_HOMEPAGE_CONFIG
  6. PTP_STREAK_CONFIG

Proceed with campaign setup? [Y/n]: y
```

### Step 8: Processing (Step 7/7)
```
╭──────────────────────────────────────────────────────────╮
│ Step 7/7: Processing Campaign                           │
╰──────────────────────────────────────────────────────────╯

✓ Created session folder: .../2026-01-03_upi_streak_7

Fetching configs from API...
⠋ Fetching STREAK_ELIGIBILITY...
✓ Fetched STREAK_ELIGIBILITY
✓ Fetched STREAK_TXN_ELIGIBILITY
✓ Fetched STREAK_CONFIG
✓ Fetched STREAK_BLOCK_TEMPLATE
✓ Fetched SCAN_HOMEPAGE_CONFIG
✓ Fetched PTP_STREAK_CONFIG

Processing configs...
⠋ Processing STREAK_ELIGIBILITY...
✓ Processed STREAK_ELIGIBILITY
✓ Processed STREAK_TXN_ELIGIBILITY
✓ Processed STREAK_CONFIG
✓ Processed STREAK_BLOCK_TEMPLATE
✓ Processed SCAN_HOMEPAGE_CONFIG
✓ Processed PTP_STREAK_CONFIG

✓ Generated campaign_info.txt
```

### Step 9: Completion
```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         ✨ Campaign Setup Complete! ✨                  ║
║                                                          ║
║  Session Folder:                                         ║
║  /Users/.../backups/2026-01-03_upi_streak_7             ║
║                                                          ║
║  Configs Processed: 6                                    ║
║  All files are ready for review                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Step 10: POST Confirmation (Double Confirmation)
```
POST to Production

⚠  This will modify the LIVE production system
⚠  6 configs will be posted

Do you want to POST these configs to production now? [y/N]: y

The script will:
  1. POST each config one by one
  2. Show success/failure for each
  3. Verify changes by fetching configs again
  4. Save verification files

Are you ABSOLUTELY SURE you want to proceed? [y/N]: y

[... posting configs ...]

✨ Campaign is now LIVE in production! ✨

✨ Done! ✨
```

## Key Features

1. **Color-coded prompts**
   - Cyan for questions
   - Green for success
   - Yellow for warnings
   - Red for errors

2. **Smart defaults**
   - Common values pre-filled
   - Press Enter to accept
   - Easy to override

3. **Tables for selection**
   - Beautiful formatted tables
   - Easy to scan options
   - Clear numbering

4. **Progress indicators**
   - Spinning animations during API calls
   - Checkmarks when complete
   - Clear status updates

5. **Double confirmation**
   - Two separate "yes" prompts before POST
   - Clear warnings about production
   - Easy to cancel

6. **Summary preview**
   - See everything before processing
   - Confirm before proceeding
   - No surprises

## Running It

### Standalone (Anyone can use it)
```bash
cd ~/documents/campaign_setup
python3 ui_enhanced.py
```

### Through Claude Code (Get help if stuck)
In Claude Code, just say:
```
"Run the enhanced UI for campaign setup"
```

And I'll execute it and help if anything goes wrong!

## What You Need

- Python 3.6+
- `rich` library (auto-installed on first run)
- API credentials (stored after first use)

That's it! No Claude Code required, but helpful if you want AI assistance.
