#!/usr/bin/env python3
"""
Master Campaign Setup Script
Collects all inputs upfront and processes all configs automatically.

Currently supports: 4 of 7 configs
- STREAK_ELIGIBILITY
- STREAK_TXN_ELIGIBILITY
- STREAK_CONFIG
- STREAK_BLOCK_TEMPLATE

Will be updated after documenting remaining 3 configs.
"""

import json
import os
import sys
import subprocess
from datetime import datetime

# ============================================================================
# STEP 1: INPUT COLLECTION
# ============================================================================

def collect_inputs():
    """Collect all required inputs from user"""

    print("="*70)
    print("CAMPAIGN SETUP - INPUT COLLECTION")
    print("="*70)
    print()

    inputs = {}

    # Basic campaign info
    print("BASIC INFORMATION:")
    inputs['campaign_name'] = input("Campaign Name (e.g., upi_streak_5): ").strip()
    inputs['campaign_id'] = input("Campaign ID (UUID): ").strip()

    print()
    print("CAMPAIGN PARAMETERS:")

    # Campaign type
    while True:
        campaign_type = input("Campaign Type (UPI/SNP/P2P): ").strip().upper()
        if campaign_type in ['UPI', 'SNP', 'P2P']:
            inputs['campaign_type'] = campaign_type
            break
        print("  Invalid. Must be UPI, SNP, or P2P")

    # Duration
    while True:
        try:
            duration = int(input("Duration (days): ").strip())
            inputs['duration_days'] = duration
            break
        except ValueError:
            print("  Invalid. Must be a number")

    # Max allowed
    while True:
        try:
            max_allowed = int(input("Max Allowed (transactions): ").strip())
            inputs['max_allowed'] = max_allowed
            break
        except ValueError:
            print("  Invalid. Must be a number")

    # Min transaction amount
    while True:
        try:
            min_amount = int(input("Min Transaction Amount: ").strip())
            inputs['min_txn_amount'] = min_amount
            break
        except ValueError:
            print("  Invalid. Must be a number")

    print()
    print("SPECIAL REQUIREMENTS:")

    # RuPay
    rupay = input("Is this a RuPay campaign? (yes/no): ").strip().lower()
    inputs['is_rupay'] = (rupay == 'yes')

    # Bank-specific
    bank_specific = input("Is this bank-specific? (yes/no): ").strip().lower()
    if bank_specific == 'yes':
        inputs['issuer_code'] = input("  Bank Issuer Code: ").strip()
    else:
        inputs['issuer_code'] = None

    print()
    print("STREAK_BLOCK_TEMPLATE CONFIGURATION:")

    # Total campaign offer
    inputs['total_offer'] = input("Total Campaign Offer (e.g., 'Rs 50 on 5 payments'): ").strip()

    # Calculate per-transaction reward
    per_txn = inputs['max_allowed']
    if 'on' in inputs['total_offer'].lower():
        # Extract amount from offer (e.g., "Rs 50" from "Rs 50 on 5 payments")
        import re
        match = re.search(r'Rs?\s*(\d+)', inputs['total_offer'], re.IGNORECASE)
        if match:
            total_amount = int(match.group(1))
            per_txn = total_amount // inputs['max_allowed']

    print(f"  → Per-transaction reward: Rs {per_txn}")
    confirm = input(f"  Is this correct? (yes/no): ").strip().lower()
    if confirm != 'yes':
        while True:
            try:
                per_txn = int(input("  Enter correct per-transaction amount: ").strip())
                break
            except ValueError:
                print("    Invalid. Must be a number")

    inputs['per_txn_reward'] = per_txn

    # Bottom sheet subtitle
    print()
    print("  Bottom Sheet Subtitle options:")
    print("  1. make a QR payment to \\nany merchant and claim cashback")
    print("  2. make a UPI payment to any merchant\\nor contact and claim cashback")
    print("  3. <format>make a UPI payment to claim assured <icon>INR</icon>{amount} cashback</format>")
    print("  4. Custom (you'll type it)")

    while True:
        choice = input("  Select (1-4): ").strip()
        if choice == '1':
            inputs['bottom_sheet_subtitle'] = "make a QR payment to \\\\nany merchant and claim cashback"
            break
        elif choice == '2':
            inputs['bottom_sheet_subtitle'] = "make a UPI payment to any merchant\\\\nor contact and claim cashback"
            break
        elif choice == '3':
            inputs['bottom_sheet_subtitle'] = f"<format>make a UPI payment to claim assured <icon>INR</icon>{per_txn} cashback</format>"
            break
        elif choice == '4':
            inputs['bottom_sheet_subtitle'] = input("  Enter custom subtitle: ").strip()
            break
        else:
            print("    Invalid choice")

    # Banner URL - try to match from mapping
    print()
    print("  Matching banner from offer...")
    banner_url = match_banner_url(inputs['total_offer'])

    if banner_url:
        print(f"  ✓ Found matching banner:")
        print(f"    {banner_url}")
        confirm = input("  Use this banner? (yes/no): ").strip().lower()
        if confirm == 'yes':
            inputs['banner_url'] = banner_url
        else:
            inputs['banner_url'] = input("  Enter banner URL: ").strip()
    else:
        print("  ✗ No matching banner found")
        inputs['banner_url'] = input("  Enter banner URL: ").strip()

    print()
    print("="*70)
    print("INPUT COLLECTION COMPLETE")
    print("="*70)

    return inputs


def match_banner_url(offer_text):
    """Match offer text to existing banner URLs"""

    # Mapping from STREAK_BLOCK_TEMPLATE_banner_mapping.md
    banner_mapping = {
        "rs 50 on 5": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/snp_streak_bottomsheet.png",
        "rs 30 on 3": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/p2p_streak_bottomsheet.png",
        "rs 25 on next": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/ae1b9ee0b0aa11f0a681e91487a04e70.png",
        "rs 100 on 5": "https://d2tecn3vwkchpd.cloudfront.net/fabrik/patterns/upi_streak_bottomsheet.png",
        "rs 125 on 5": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/b227653057ec11f0b48d3dc3d0510fdd.png",
        "rs 50 on next": "https://d1sofudel0ufia.cloudfront.net/fabrik/alerts/jul_24_streak_reward.png",
        "rs 30 on next": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/e63d83f0559311f0bb81c90da4aa3b71.png",
        "rs 10 on next": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/727ca8e0ab4911f0b91999bd5d4e25a3.png",
        "rs 75 on 5": "https://d704ayip06922.cloudfront.net/prod-rewards-assets-data/f4a718d0b94c11f09808a11c11c6fd56.png",
    }

    # Normalize offer text
    normalized = offer_text.lower().strip()
    # Remove "payments", "payment", "cashback" etc
    normalized = normalized.replace('payments', '').replace('payment', '').replace('cashback', '').strip()

    return banner_mapping.get(normalized)


# ============================================================================
# STEP 2: SETUP SESSION
# ============================================================================

def setup_session(inputs):
    """Create backup folder structure"""

    date_str = datetime.now().strftime("%Y-%m-%d")
    campaign_name = inputs['campaign_name']

    session_folder = f"/Users/anurupojha/Documents/campaign_setup/backups/{date_str}_{campaign_name}"

    os.makedirs(session_folder, exist_ok=True)

    print(f"\n✓ Created session folder: {session_folder}")

    return session_folder


def save_campaign_info(session_folder, inputs):
    """Save campaign_info.txt"""

    info_file = os.path.join(session_folder, "campaign_info.txt")

    with open(info_file, 'w') as f:
        f.write("Campaign Setup Session\n")
        f.write("======================\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"Campaign Name: {inputs['campaign_name']}\n")
        f.write(f"Campaign ID: {inputs['campaign_id']}\n\n")

        f.write("Campaign Details:\n")
        f.write("-----------------\n")
        f.write(f"- Type: {inputs['campaign_type']}\n")
        f.write(f"- Duration: {inputs['duration_days']} days\n")
        f.write(f"- Max Allowed: {inputs['max_allowed']} transactions\n")
        f.write(f"- Min Transaction Amount: {inputs['min_txn_amount']}\n")
        f.write(f"- RuPay Campaign: {'Yes' if inputs['is_rupay'] else 'No'}\n")
        f.write(f"- Bank-Specific: {'Yes - ' + inputs['issuer_code'] if inputs['issuer_code'] else 'No'}\n")
        f.write(f"- Total Offer: {inputs['total_offer']}\n")
        f.write(f"- Per-Transaction Reward: Rs {inputs['per_txn_reward']}\n\n")

        f.write("Configs Modified:\n")
        f.write("-----------------\n")
        f.write("1. STREAK_ELIGIBILITY - ✓ Modified (not posted yet)\n")
        f.write("2. STREAK_TXN_ELIGIBILITY - ✓ Modified (not posted yet)\n")
        f.write("3. STREAK_CONFIG - ✓ Modified (not posted yet)\n")
        f.write("4. STREAK_BLOCK_TEMPLATE - ✓ Modified (not posted yet)\n")
        f.write("5. SCAN_HOMEPAGE_CONFIG - Pending (config not yet documented)\n")
        f.write("6. EXPERIMENT_ID_LIST - Pending (config not yet documented)\n")
        f.write("7. PTP_STREAK_CONFIG - Pending (config not yet documented)\n\n")

        f.write("Notes:\n")
        f.write("------\n")
        f.write("- Generated by master setup script\n")
        f.write("- cross_beneficiary_name_check_enabled: false (default)\n")

    print(f"✓ Saved campaign info")


# ============================================================================
# STEP 3: PROCESS CONFIGS
# ============================================================================

def fetch_config(config_key, session_folder):
    """Fetch config via curl and save to before.json"""

    url = f"http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template/{config_key}"
    headers = {
        'userid': '96cc31b5-2f09-4b22-8f93-d6e46177a84d',
        '_cred_apikey': '6d5ddcbedf09bd6a4a2651cd3bd8f1eca259e606979c0e2766c9548724dbe23e'
    }

    output_file = os.path.join(session_folder, f"{config_key}_before.json")

    # Build curl command
    cmd = [
        'curl', '-s', url,
        '--header', f'userid: {headers["userid"]}',
        '--header', f'_cred_apikey: {headers["_cred_apikey"]}'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        # Validate JSON
        try:
            json.loads(result.stdout)
            with open(output_file, 'w') as f:
                f.write(result.stdout)
            print(f"  ✓ Fetched {config_key}")
            return True
        except json.JSONDecodeError:
            print(f"  ✗ Invalid JSON response for {config_key}")
            return False
    else:
        print(f"  ✗ Failed to fetch {config_key}")
        return False


def process_configs(session_folder, inputs):
    """Process all 4 configs"""

    print("\n" + "="*70)
    print("PROCESSING CONFIGS")
    print("="*70)

    scripts_dir = "/Users/anurupojha/Documents/campaign_setup/scripts"

    # Config 1: STREAK_ELIGIBILITY
    print("\n[1/4] STREAK_ELIGIBILITY")
    if fetch_config("STREAK_ELIGIBILITY", session_folder):
        cmd = [
            'python3',
            os.path.join(scripts_dir, 'process_streak_eligibility.py'),
            os.path.join(session_folder, 'STREAK_ELIGIBILITY_before.json'),
            os.path.join(session_folder, 'STREAK_ELIGIBILITY_after_unescaped.json'),
            os.path.join(session_folder, 'STREAK_ELIGIBILITY_after.json'),
            inputs['campaign_name'],
            inputs['campaign_type'],
            str(inputs['duration_days']),
            str(inputs['max_allowed'])
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Processed")
        else:
            print(f"  ✗ Error: {result.stderr}")

    # Config 2: STREAK_TXN_ELIGIBILITY
    print("\n[2/4] STREAK_TXN_ELIGIBILITY")
    if fetch_config("STREAK_TXN_ELIGIBILITY", session_folder):
        cmd = [
            'python3',
            os.path.join(scripts_dir, 'process_txn_eligibility.py'),
            os.path.join(session_folder, 'STREAK_TXN_ELIGIBILITY_before.json'),
            os.path.join(session_folder, 'STREAK_TXN_ELIGIBILITY_after_unescaped.json'),
            os.path.join(session_folder, 'STREAK_TXN_ELIGIBILITY_after.json'),
            inputs['campaign_name'],
            inputs['campaign_type'],
            str(inputs['min_txn_amount']),
            'true' if inputs['is_rupay'] else 'false',
            inputs['issuer_code'] if inputs['issuer_code'] else ''
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Processed")
        else:
            print(f"  ✗ Error: {result.stderr}")

    # Config 3: STREAK_CONFIG
    print("\n[3/4] STREAK_CONFIG")
    if fetch_config("STREAK_CONFIG", session_folder):
        cmd = [
            'python3',
            os.path.join(scripts_dir, 'process_streak_config.py'),
            os.path.join(session_folder, 'STREAK_CONFIG_before.json'),
            os.path.join(session_folder, 'STREAK_CONFIG_after_unescaped.json'),
            os.path.join(session_folder, 'STREAK_CONFIG_after.json'),
            inputs['campaign_id']
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Processed")
        else:
            print(f"  ✗ Error: {result.stderr}")

    # Config 4: STREAK_BLOCK_TEMPLATE
    print("\n[4/4] STREAK_BLOCK_TEMPLATE")
    if fetch_config("STREAK_BLOCK_TEMPLATE", session_folder):
        cmd = [
            'python3',
            os.path.join(scripts_dir, 'process_streak_block_template.py'),
            os.path.join(session_folder, 'STREAK_BLOCK_TEMPLATE_before.json'),
            os.path.join(session_folder, 'STREAK_BLOCK_TEMPLATE_after_unescaped.txt'),
            os.path.join(session_folder, 'STREAK_BLOCK_TEMPLATE_after.json'),
            inputs['campaign_id'],
            inputs['banner_url'],
            f"<format>earn <icon>INR</icon>{inputs['per_txn_reward']}</format>",
            inputs['bottom_sheet_subtitle']
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Processed")
        else:
            print(f"  ✗ Error: {result.stderr}")

    print("\n" + "="*70)
    print("PROCESSING COMPLETE")
    print("="*70)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*70)
    print("MASTER CAMPAIGN SETUP SCRIPT")
    print("Supports: 4 of 7 configs (will update after documenting remaining 3)")
    print("="*70 + "\n")

    # Step 1: Collect inputs
    inputs = collect_inputs()

    # Step 2: Setup session
    session_folder = setup_session(inputs)
    save_campaign_info(session_folder, inputs)

    # Step 3: Process configs
    process_configs(session_folder, inputs)

    print(f"\n✓ Campaign setup complete!")
    print(f"✓ Session folder: {session_folder}")
    print(f"\n⚠️  IMPORTANT: Review all *_after.json files before posting!")
    print(f"⚠️  Currently supports 4 of 7 configs. Remaining 3 configs need manual setup.\n")


if __name__ == "__main__":
    main()
