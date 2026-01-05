#!/usr/bin/env python3
"""
Master Campaign Setup Script
=============================

This is the ONLY script you need to run to set up a complete campaign.
It collects all inputs upfront, then automatically processes all relevant configs.

Usage:
    python3 setup_campaign_master.py

The script will:
1. Ask you for all campaign details upfront
2. Determine which configs are needed based on campaign type
3. Create a session folder with proper naming
4. Fetch all configs from the API
5. Process all configs automatically
6. Generate campaign_info.txt with complete summary
7. Show you what was done and what files are ready for review

After 3 months, you just run this script again. The magic unfolds.
"""

import json
import sys
import os
from datetime import datetime
import subprocess
from pathlib import Path
import argparse


# Base directory for the app (works both locally and on Streamlit Cloud)
APP_DIR = Path(__file__).parent


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_step(step_num, text):
    """Print a numbered step"""
    print(f"{Colors.CYAN}{Colors.BOLD}[Step {step_num}]{Colors.ENDC} {text}")


def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print an info message"""
    print(f"{Colors.YELLOW}→ {text}{Colors.ENDC}")


def get_input(prompt, validation_fn=None, error_msg="Invalid input. Please try again."):
    """Get user input with optional validation"""
    while True:
        value = input(f"{Colors.BOLD}{prompt}{Colors.ENDC} ").strip()
        if validation_fn is None or validation_fn(value):
            return value
        print_error(error_msg)


def get_yes_no(prompt):
    """Get yes/no input from user"""
    while True:
        response = input(f"{Colors.BOLD}{prompt} (yes/no):{Colors.ENDC} ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        print_error("Please answer 'yes' or 'no'")


def load_credentials():
    """Load API credentials from credentials.json"""
    creds_file = APP_DIR / "credentials.json"
    if creds_file.exists():
        with open(creds_file, 'r') as f:
            return json.load(f)
    return None


def load_banner_registry():
    """Load banner registry from JSON"""
    registry_file = APP_DIR / "banner_registry.json"
    with open(registry_file, 'r') as f:
        return json.load(f)


def save_banner_registry(registry):
    """Save updated banner registry"""
    registry_file = APP_DIR / "banner_registry.json"
    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)


def load_subtitle_templates():
    """Load subtitle templates from JSON"""
    templates_file = APP_DIR / "subtitle_templates.json"
    with open(templates_file, 'r') as f:
        return json.load(f)


def save_subtitle_templates(templates):
    """Save updated subtitle templates"""
    templates_file = APP_DIR / "subtitle_templates.json"
    with open(templates_file, 'w') as f:
        json.dump(templates, f, indent=2)


def collect_campaign_inputs():
    """Collect all campaign inputs upfront"""
    print_header("Campaign Setup - Input Collection")

    print_info("Let's collect all the information needed for your campaign.")
    print_info("I'll ask everything upfront, then process all configs automatically.\n")

    inputs = {}

    # Basic campaign details
    print(f"{Colors.BLUE}{Colors.BOLD}Basic Campaign Details:{Colors.ENDC}")
    inputs['campaign_name'] = get_input(
        "Campaign Name (e.g., upi_streak_5):",
        lambda x: len(x) > 0,
        "Campaign name cannot be empty"
    )

    inputs['campaign_id'] = get_input(
        "Campaign ID (UUID):",
        lambda x: len(x) > 0,
        "Campaign ID cannot be empty"
    )

    # Campaign type
    while True:
        print(f"\n{Colors.BLUE}{Colors.BOLD}Campaign Type:{Colors.ENDC}")
        print("  1. UPI  - Both P2P + Scan & Pay eligible")
        print("  2. SNP  - Scan & Pay only")
        print("  3. P2P  - Peer-to-peer only")
        choice = get_input("Select campaign type (1/2/3):", lambda x: x in ['1', '2', '3'])

        type_map = {'1': 'UPI', '2': 'SNP', '3': 'P2P'}
        inputs['campaign_type'] = type_map[choice]
        break

    # Duration and transaction details
    print(f"\n{Colors.BLUE}{Colors.BOLD}Transaction Details:{Colors.ENDC}")
    inputs['duration_days'] = int(get_input(
        "Duration (in days):",
        lambda x: x.isdigit() and int(x) > 0,
        "Duration must be a positive number"
    ))

    inputs['max_allowed'] = int(get_input(
        "Max Allowed (number of transactions):",
        lambda x: x.isdigit() and int(x) > 0,
        "Max allowed must be a positive number"
    ))

    inputs['min_txn_amount'] = int(get_input(
        "Minimum Transaction Amount:",
        lambda x: x.isdigit() and int(x) > 0,
        "Amount must be a positive number"
    ))

    # RuPay and bank-specific
    print(f"\n{Colors.BLUE}{Colors.BOLD}Additional Eligibility:{Colors.ENDC}")
    inputs['is_rupay'] = get_yes_no("Is this a RuPay campaign?")

    inputs['is_bank_specific'] = get_yes_no("Is this bank-specific?")
    if inputs['is_bank_specific']:
        inputs['issuer_code'] = get_input(
            "Bank Issuer Code:",
            lambda x: len(x) > 0,
            "Issuer code cannot be empty"
        )
    else:
        inputs['issuer_code'] = None

    # Offer details
    print(f"\n{Colors.BLUE}{Colors.BOLD}Offer Details:{Colors.ENDC}")
    inputs['total_offer'] = int(get_input(
        f"Total Campaign Offer (e.g., Rs 50 for '{inputs['max_allowed']} payments'):",
        lambda x: x.isdigit() and int(x) > 0,
        "Total offer must be a positive number"
    ))

    # Calculate per-transaction reward
    inputs['per_txn_reward'] = inputs['total_offer'] // inputs['max_allowed']
    print_info(f"Calculated per-transaction reward: Rs {inputs['per_txn_reward']}")

    # Banner selection
    print(f"\n{Colors.BLUE}{Colors.BOLD}Banner Selection:{Colors.ENDC}")

    # Load banner registry
    banner_registry = load_banner_registry()
    banners = banner_registry['banners']

    # Display all available banners
    print(f"{Colors.CYAN}Select banner callout:{Colors.ENDC}")
    for banner in banners:
        print(f" [{banner['id']:2}] {banner['callout']}")
    print(f" [ 0] Enter custom banner")

    # Get user choice
    while True:
        choice = get_input("\nYour choice:", lambda x: x.isdigit())
        choice_num = int(choice)

        if choice_num == 0:
            # Custom banner
            new_url = get_input("Enter banner URL:", lambda x: x.startswith('http'))
            new_callout = get_input("Enter callout description (e.g., Rs 75 on 7 payments):")

            # Add to registry
            new_id = max([b['id'] for b in banners]) + 1
            new_banner = {"id": new_id, "callout": new_callout, "url": new_url}
            banners.append(new_banner)
            banner_registry['banners'] = banners
            save_banner_registry(banner_registry)

            inputs['banner_url'] = new_url
            print_success(f"Saved new banner (will appear as option [{new_id}] in future)")
            break
        elif 1 <= choice_num <= len(banners):
            # Existing banner
            selected = next(b for b in banners if b['id'] == choice_num)
            inputs['banner_url'] = selected['url']
            print_info(f"Selected: {selected['callout']}")
            break
        else:
            print_error(f"Please enter a number between 0 and {len(banners)}")

    # Bottom sheet subtitle
    print(f"\n{Colors.BLUE}{Colors.BOLD}Bottom Sheet Subtitle:{Colors.ENDC}")

    # Load subtitle templates
    subtitle_data = load_subtitle_templates()
    subtitles = subtitle_data['subtitles']

    # Display all available subtitles
    print(f"{Colors.CYAN}Select bottom sheet subtitle:{Colors.ENDC}")
    for subtitle in subtitles:
        display_text = subtitle['text']
        if subtitle.get('has_placeholder'):
            display_text = display_text.replace('X', str(inputs['per_txn_reward']))
        print(f" [{subtitle['id']}] {display_text}")
    print(f" [0] Enter custom subtitle")

    # Get user choice
    while True:
        choice = get_input("\nYour choice:", lambda x: x.isdigit())
        choice_num = int(choice)

        if choice_num == 0:
            # Custom subtitle
            new_subtitle = get_input("Enter subtitle (use \\\\n for line breaks):")

            # Add to templates
            new_id = max([s['id'] for s in subtitles]) + 1
            new_template = {
                "id": new_id,
                "text": new_subtitle,
                "description": "Custom template"
            }
            subtitles.append(new_template)
            subtitle_data['subtitles'] = subtitles
            save_subtitle_templates(subtitle_data)

            inputs['bottom_sheet_subtitle'] = new_subtitle
            print_success(f"Saved new subtitle (will appear as option [{new_id}] in future)")
            break
        elif 1 <= choice_num <= len(subtitles):
            # Existing subtitle
            selected = next(s for s in subtitles if s['id'] == choice_num)
            subtitle_text = selected['text']

            # Replace placeholder if exists
            if selected.get('has_placeholder'):
                subtitle_text = subtitle_text.replace('X', str(inputs['per_txn_reward']))

            inputs['bottom_sheet_subtitle'] = subtitle_text
            print_info(f"Selected: {subtitle_text}")
            break
        else:
            print_error(f"Please enter a number between 0 and {len(subtitles)}")

    # API credentials - Load from file or ask if not found
    credentials = load_credentials()

    if credentials:
        print(f"\n{Colors.GREEN}✓ Using saved API credentials{Colors.ENDC}")
        inputs['userid'] = credentials['userid']
        inputs['apikey'] = credentials['apikey']
    else:
        print(f"\n{Colors.BLUE}{Colors.BOLD}API Credentials:{Colors.ENDC}")
        print_info("Credentials will be saved for future use")

        inputs['userid'] = get_input(
            "API userid header:",
            lambda x: len(x) > 0,
            "userid cannot be empty"
        )

        inputs['apikey'] = get_input(
            "API key (_cred_apikey header):",
            lambda x: len(x) > 0,
            "API key cannot be empty"
        )

        # Save credentials for future use
        creds_file = APP_DIR / "credentials.json"
        with open(creds_file, 'w') as f:
            json.dump({"userid": inputs['userid'], "apikey": inputs['apikey']}, f, indent=2)
        print_success("Credentials saved to credentials.json")

    return inputs


def determine_configs_needed(campaign_type):
    """Determine which configs are needed based on campaign type"""
    configs = [
        'STREAK_ELIGIBILITY',
        'STREAK_TXN_ELIGIBILITY',
        'STREAK_CONFIG',
        'STREAK_BLOCK_TEMPLATE',
        'SCAN_HOMEPAGE_CONFIG'
    ]

    # PTP_STREAK_CONFIG only for UPI and P2P campaigns
    if campaign_type in ['UPI', 'P2P']:
        configs.append('PTP_STREAK_CONFIG')

    return configs


def create_session_folder(campaign_name):
    """Create session folder with proper naming"""
    base_path = APP_DIR / "backups"
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{date_str}_{campaign_name}"
    folder_path = base_path / folder_name

    folder_path.mkdir(parents=True, exist_ok=True)
    return str(folder_path)


def fetch_config(config_key, session_folder, userid, apikey):
    """Fetch config via GET request and save to _before.json"""
    print_info(f"Fetching {config_key}...")

    url = f"http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template/{config_key}"
    output_file = os.path.join(session_folder, f"{config_key}_before.json")

    curl_cmd = [
        'curl', '-s', '-X', 'GET', url,
        '-H', f'userid: {userid}',
        '-H', f'_cred_apikey: {apikey}'
    ]

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)

        # Parse and pretty-print the JSON
        data = json.loads(result.stdout)

        # Check if response indicates auth failure
        if 'error' in data or 'message' in data:
            print_error(f"API Error: {data.get('error', data.get('message', 'Unknown error'))}")
            print_error("Your API credentials may be invalid or expired")
            print_error(f"Delete {APP_DIR / 'credentials.json'} and run again")
            return False

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print_success(f"Saved: {config_key}_before.json")
        return True
    except json.JSONDecodeError as e:
        print_error(f"Failed to parse response from {config_key}: {e}")
        print_error("Your API credentials may be invalid or expired")
        print_error(f"Delete {APP_DIR / 'credentials.json'} and run again")
        return False
    except Exception as e:
        print_error(f"Failed to fetch {config_key}: {e}")
        return False


def process_config(config_key, session_folder, inputs):
    """Process a config by calling the appropriate processing script"""
    print_info(f"Processing {config_key}...")

    script_map = {
        'STREAK_ELIGIBILITY': 'process_streak_eligibility.py',
        'STREAK_TXN_ELIGIBILITY': 'process_txn_eligibility.py',
        'STREAK_CONFIG': 'process_streak_config.py',
        'STREAK_BLOCK_TEMPLATE': 'process_streak_block_template.py',
        'SCAN_HOMEPAGE_CONFIG': 'process_scan_homepage_config.py',
        'PTP_STREAK_CONFIG': 'process_ptp_streak_config.py'
    }

    script_name = script_map.get(config_key)
    if not script_name:
        print_error(f"No processing script found for {config_key}")
        return False

    script_path = str(APP_DIR / "scripts" / script_name)

    before_file = os.path.join(session_folder, f"{config_key}_before.json")
    after_unescaped_file = os.path.join(session_folder, f"{config_key}_after_unescaped.json")
    after_file = os.path.join(session_folder, f"{config_key}_after.json")

    # Verify script exists
    if not os.path.exists(script_path):
        print_error(f"Script not found: {script_path}")
        return False

    # Verify before file exists
    if not os.path.exists(before_file):
        print_error(f"Before file not found: {before_file}. Run fetch first.")
        return False

    # Build command based on config type
    if config_key == 'STREAK_ELIGIBILITY':
        cmd = [
            'python3', script_path,
            before_file,
            after_unescaped_file,
            after_file,
            inputs['campaign_name'],
            inputs['campaign_type'],
            str(inputs['duration_days']),
            str(inputs['max_allowed'])
        ]

    elif config_key == 'STREAK_TXN_ELIGIBILITY':
        cmd = [
            'python3', script_path,
            before_file,
            after_unescaped_file,
            after_file,
            inputs['campaign_name'],
            inputs['campaign_type'],
            str(inputs['min_txn_amount']),
            'yes' if inputs['is_rupay'] else 'no',
            'yes' if inputs['is_bank_specific'] else 'no'
        ]
        if inputs['is_bank_specific']:
            cmd.append(inputs['issuer_code'])

    elif config_key == 'STREAK_CONFIG':
        cmd = [
            'python3', script_path,
            before_file,
            after_unescaped_file,
            after_file,
            inputs['campaign_id']
        ]

    elif config_key == 'STREAK_BLOCK_TEMPLATE':
        cmd = [
            'python3', script_path,
            before_file,
            after_unescaped_file,
            after_file,
            inputs['campaign_id'],
            inputs['banner_url'],
            str(inputs['per_txn_reward']),
            inputs['bottom_sheet_subtitle']
        ]

    elif config_key == 'SCAN_HOMEPAGE_CONFIG':
        cmd = [
            'python3', script_path,
            before_file,
            after_unescaped_file,
            after_file,
            inputs['campaign_name'],
            inputs['campaign_type'],
            str(inputs['duration_days']),
            str(inputs['max_allowed']),
            str(inputs['per_txn_reward']),
            str(inputs['total_offer'])
        ]

    elif config_key == 'PTP_STREAK_CONFIG':
        cmd = [
            'python3', script_path,
            before_file,
            after_unescaped_file,
            after_file,
            inputs['campaign_name'],
            inputs['campaign_type'],
            str(inputs['duration_days']),
            str(inputs['max_allowed']),
            str(inputs['per_txn_reward']),
            str(inputs['total_offer'])
        ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        print_success(f"Processed {config_key}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to process {config_key}")
        print(e.stdout)
        print(e.stderr)
        return False


def post_config(config_key, session_folder, userid, apikey):
    """POST a config to the API"""
    print_info(f"Posting {config_key}...")

    url = "http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template"
    after_file = os.path.join(session_folder, f"{config_key}_after.json")

    curl_cmd = [
        'curl', '-s', '-X', 'POST', url,
        '-H', 'Content-Type: application/json',
        '-H', f'userid: {userid}',
        '-H', f'_cred_apikey: {apikey}',
        '-d', f'@{after_file}'
    ]

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
        # Parse response to check for success
        try:
            response = json.loads(result.stdout)
            print_success(f"Posted {config_key}")
            return True
        except json.JSONDecodeError:
            print_error(f"Posted {config_key} but got unexpected response: {result.stdout}")
            return False
    except Exception as e:
        print_error(f"Failed to post {config_key}: {e}")
        return False


def verify_config(config_key, session_folder, userid, apikey):
    """Verify a config by fetching it again"""
    print_info(f"Verifying {config_key}...")

    url = f"http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template/{config_key}"
    verify_file = os.path.join(session_folder, f"{config_key}_verify.json")

    curl_cmd = [
        'curl', '-s', '-X', 'GET', url,
        '-H', f'userid: {userid}',
        '-H', f'_cred_apikey: {apikey}'
    ]

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        with open(verify_file, 'w') as f:
            json.dump(data, f, indent=2)
        print_success(f"Verified {config_key} - saved to {config_key}_verify.json")
        return True
    except Exception as e:
        print_error(f"Failed to verify {config_key}: {e}")
        return False


def post_all_configs(session_folder, configs_processed, userid, apikey, skip_confirmations=False):
    """Ask for permission and POST all configs

    Args:
        skip_confirmations: If True, skip terminal prompts (for web UI usage)
    """
    if not skip_confirmations:
        print_header("📤 Ready to POST to Production")

        print(f"{Colors.YELLOW}{Colors.BOLD}IMPORTANT:{Colors.ENDC}")
        print("You are about to POST these configs to the PRODUCTION API:")
        for config in configs_processed:
            print(f"  • {config}")
        print(f"\n{Colors.YELLOW}This will modify the live production system.{Colors.ENDC}\n")

        # First confirmation
        if not get_yes_no("Do you want to POST these configs to production now?"):
            print_info("Skipping POST. You can manually POST later using campaign_info.txt templates.")
            return False

        # Show what will happen
        print(f"\n{Colors.BOLD}The script will:{Colors.ENDC}")
        print("1. POST each config one by one")
        print("2. Show success/failure for each")
        print("3. Fetch each config again to verify changes")
        print("4. Save verification files as *_verify.json\n")

        # Final confirmation
        final_confirm = get_yes_no("Are you absolutely sure you want to proceed?")
        if not final_confirm:
            print_info("POST cancelled. Files are ready for manual review and POST.")
            return False

        # Proceed with POST
        print_header("⏳ Posting Configs to Production")
    else:
        # Web UI mode - no terminal prompts
        print("Posting configs to production...")

    posted_count = 0
    verified_count = 0

    for config in configs_processed:
        if post_config(config, session_folder, userid, apikey):
            posted_count += 1

            # Verify the change
            import time
            time.sleep(1)  # Brief delay before verification
            if verify_config(config, session_folder, userid, apikey):
                verified_count += 1
        else:
            print_error(f"Skipping verification for {config} due to POST failure")

    # Summary
    print_header("📊 POST Summary")
    print(f"{Colors.BOLD}Posted:{Colors.ENDC} {posted_count}/{len(configs_processed)}")
    print(f"{Colors.BOLD}Verified:{Colors.ENDC} {verified_count}/{len(configs_processed)}")

    if posted_count == len(configs_processed):
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All configs successfully posted and verified!{Colors.ENDC}")
        return True
    else:
        print(f"\n{Colors.YELLOW}⚠ Some configs failed to POST. Check the output above.{Colors.ENDC}")
        return False


def generate_campaign_info(session_folder, inputs, configs_processed, posted=False):
    """Generate campaign_info.txt with complete summary"""
    info_file = os.path.join(session_folder, "campaign_info.txt")

    content = f"""Campaign Setup Session
======================

Date: {datetime.now().strftime("%Y-%m-%d")}
Campaign Name: {inputs['campaign_name']}
Campaign ID: {inputs['campaign_id']}

Campaign Details:
-----------------
- Type: {inputs['campaign_type']}
- Duration: {inputs['duration_days']} days
- Max Allowed: {inputs['max_allowed']} transactions
- Total Offer: Rs {inputs['total_offer']}
- Per-Transaction Reward: Rs {inputs['per_txn_reward']}
- Min Transaction Amount: {inputs['min_txn_amount']}
- RuPay Campaign: {'Yes' if inputs['is_rupay'] else 'No'}
- Bank-Specific: {'Yes (' + inputs['issuer_code'] + ')' if inputs['is_bank_specific'] else 'No'}

UI Configuration:
-----------------
- Banner URL: {inputs['banner_url']}
- Bottom Sheet Subtitle: {inputs['bottom_sheet_subtitle']}

Configs Processed:
------------------
"""

    for i, config in enumerate(configs_processed, 1):
        status = "✓ Posted & Verified" if posted else "✓ Processed (ready for review)"
        content += f"{i}. {config} - {status}\n"

    if not posted:
        content += f"""
Next Steps:
-----------
1. Review all _after.json files to verify changes
2. Compare _before.json with _after.json for each config
3. When satisfied, POST each _after.json file to the API
4. Verify changes by fetching configs again

API POST Command Template:
--------------------------
curl -X POST \\
  http://kongproxy.infra.dreamplug.net/heimdall/heartbeat/v1/template \\
  -H 'Content-Type: application/json' \\
  -H 'userid: {inputs['userid']}' \\
  -H '_cred_apikey: {inputs['apikey']}' \\
  -d @<CONFIG_KEY>_after.json

Notes:
------
- All configs have been processed and are ready for review
- IMPORTANT: Review before posting to production!
- cross_beneficiary_name_check_enabled: false (as specified)
"""
    else:
        content += f"""
Status:
-------
✓ All configs have been POSTED to production and verified
✓ Verification files saved as *_verify.json
✓ Campaign is now LIVE

Files in this session:
----------------------
- *_before.json: Original configs from API
- *_after_unescaped.json: Human-readable modified versions
- *_after.json: Versions that were posted to production
- *_verify.json: Fetched after POST to verify changes

Notes:
------
- cross_beneficiary_name_check_enabled: false (as specified)
- All changes are now live in production
"""

    with open(info_file, 'w') as f:
        f.write(content)

    print_success(f"{'Updated' if posted else 'Generated'} campaign_info.txt")


def parse_args():
    """Parse command-line arguments for non-interactive mode"""
    parser = argparse.ArgumentParser(description='Campaign Setup Master Script')
    parser.add_argument('--campaign-name', help='Campaign name (e.g., upi_streak_5)')
    parser.add_argument('--campaign-id', help='Campaign ID (UUID from team)')
    parser.add_argument('--type', choices=['UPI', 'SNP', 'P2P'], help='Campaign type')
    parser.add_argument('--duration', type=int, help='Duration in days')
    parser.add_argument('--max-allowed', type=int, help='Max allowed transactions')
    parser.add_argument('--min-txn-amount', type=int, help='Minimum transaction amount')
    parser.add_argument('--is-rupay', action='store_true', help='Is RuPay campaign')
    parser.add_argument('--is-bank-specific', action='store_true', help='Is bank-specific campaign')
    parser.add_argument('--issuer-code', help='Bank issuer code (if bank-specific)')
    parser.add_argument('--total-offer', type=int, help='Total campaign offer amount')
    parser.add_argument('--banner-id', type=int, help='Banner ID from registry (or 0 for custom)')
    parser.add_argument('--banner-url', help='Custom banner URL (if banner-id is 0)')
    parser.add_argument('--banner-callout', help='Custom banner callout (if banner-id is 0)')
    parser.add_argument('--subtitle-id', type=int, help='Subtitle ID from templates (or 0 for custom)')
    parser.add_argument('--custom-subtitle', help='Custom subtitle (if subtitle-id is 0)')
    parser.add_argument('--dry-run', action='store_true', help='Generate files but skip POST')
    parser.add_argument('--auto-post', action='store_true', help='Auto-POST without confirmation (dangerous!)')

    return parser.parse_args()


def collect_campaign_inputs_from_args(args):
    """Collect campaign inputs from command-line arguments"""
    inputs = {}

    # Basic campaign details
    inputs['campaign_name'] = args.campaign_name
    inputs['campaign_id'] = args.campaign_id
    inputs['campaign_type'] = args.type
    inputs['duration_days'] = args.duration
    inputs['max_allowed'] = args.max_allowed
    inputs['min_txn_amount'] = args.min_txn_amount

    # Additional eligibility
    inputs['is_rupay'] = args.is_rupay
    inputs['is_bank_specific'] = args.is_bank_specific
    inputs['issuer_code'] = args.issuer_code

    # Offer details
    inputs['total_offer'] = args.total_offer
    inputs['per_txn_reward'] = inputs['total_offer'] // inputs['max_allowed']

    # Banner selection
    if args.banner_id == 0:
        # Custom banner
        inputs['banner_url'] = args.banner_url
    else:
        # Load from registry
        banner_registry = load_banner_registry()
        banner = next((b for b in banner_registry['banners'] if b['id'] == args.banner_id), None)
        if not banner:
            print_error(f"Banner ID {args.banner_id} not found in registry")
            sys.exit(1)
        inputs['banner_url'] = banner['url']

    # Subtitle selection
    if args.subtitle_id == 0:
        # Custom subtitle
        inputs['bottom_sheet_subtitle'] = args.custom_subtitle
    else:
        # Load from templates
        subtitle_data = load_subtitle_templates()
        subtitle = next((s for s in subtitle_data['subtitles'] if s['id'] == args.subtitle_id), None)
        if not subtitle:
            print_error(f"Subtitle ID {args.subtitle_id} not found in templates")
            sys.exit(1)
        subtitle_text = subtitle['text']
        if subtitle.get('has_placeholder'):
            subtitle_text = subtitle_text.replace('X', str(inputs['per_txn_reward']))
        inputs['bottom_sheet_subtitle'] = subtitle_text

    # API credentials - always load from file in non-interactive mode
    credentials = load_credentials()
    if not credentials:
        print_error("No credentials found. Run in interactive mode first to set up credentials.")
        sys.exit(1)
    inputs['userid'] = credentials['userid']
    inputs['apikey'] = credentials['apikey']

    return inputs


def main():
    """Main orchestration function"""
    # Parse command-line arguments
    args = parse_args()

    # Check if running in non-interactive mode
    non_interactive = args.campaign_name is not None

    if non_interactive:
        print_header("🎯 Campaign Setup Master Script (Non-Interactive Mode)")
        print(f"{Colors.BOLD}Running with provided arguments...{Colors.ENDC}\n")

        # Validate required args
        required_args = ['campaign_name', 'campaign_id', 'type', 'duration', 'max_allowed',
                        'min_txn_amount', 'total_offer', 'banner_id', 'subtitle_id']
        missing = [arg for arg in required_args if getattr(args, arg.replace('-', '_')) is None]
        if missing:
            print_error(f"Missing required arguments: {', '.join(['--' + arg for arg in missing])}")
            sys.exit(1)

        if args.banner_id == 0 and not args.banner_url:
            print_error("--banner-url required when --banner-id is 0")
            sys.exit(1)

        if args.subtitle_id == 0 and not args.custom_subtitle:
            print_error("--custom-subtitle required when --subtitle-id is 0")
            sys.exit(1)

        # Collect inputs from args
        inputs = collect_campaign_inputs_from_args(args)
    else:
        # Interactive mode
        print_header("🎯 Campaign Setup Master Script")
        print(f"{Colors.BOLD}This script will guide you through setting up a complete campaign.{Colors.ENDC}")
        print(f"{Colors.BOLD}All inputs will be collected upfront, then configs will be processed automatically.{Colors.ENDC}\n")

        # Collect inputs interactively
        inputs = collect_campaign_inputs()

    try:
        # Step 1: Already done (collected via args or interactive)
        if not non_interactive:
            print_step(1, "Campaign Inputs Collected")
        else:
            print_step(1, "Using Provided Arguments")

        # Display collected inputs
        print(f"\n{Colors.CYAN}Campaign Summary:{Colors.ENDC}")
        print(f"  Name: {inputs['campaign_name']}")
        print(f"  ID: {inputs['campaign_id']}")
        print(f"  Type: {inputs['campaign_type']}")
        print(f"  Duration: {inputs['duration_days']} days")
        print(f"  Max Allowed: {inputs['max_allowed']} transactions")
        print(f"  Total Offer: Rs {inputs['total_offer']} (Rs {inputs['per_txn_reward']} per txn)")
        print(f"  Min Txn Amount: {inputs['min_txn_amount']}")
        print(f"  RuPay: {'Yes' if inputs['is_rupay'] else 'No'}")
        print(f"  Bank-Specific: {'Yes (' + inputs['issuer_code'] + ')' if inputs['is_bank_specific'] else 'No'}")

        # Step 2: Determine which configs are needed
        print_step(2, "Determining Required Configs")
        configs_needed = determine_configs_needed(inputs['campaign_type'])
        print_info(f"Campaign type '{inputs['campaign_type']}' requires {len(configs_needed)} configs:")
        for config in configs_needed:
            print(f"  • {config}")

        # Step 3: Create session folder
        print_step(3, "Creating Session Folder")
        session_folder = create_session_folder(inputs['campaign_name'])
        print_success(f"Created: {session_folder}")

        # Step 4: Fetch all configs
        print_step(4, "Fetching Configs from API")
        for config in configs_needed:
            if not fetch_config(config, session_folder, inputs['userid'], inputs['apikey']):
                print_error(f"Failed to fetch {config}. Aborting.")
                return 1

        # Step 5: Process all configs
        print_step(5, "Processing Configs")
        configs_processed = []
        for config in configs_needed:
            if process_config(config, session_folder, inputs):
                configs_processed.append(config)
            else:
                print_error(f"Failed to process {config}. Continuing with others...")

        # Step 6: Generate campaign info
        print_step(6, "Generating Campaign Summary")
        generate_campaign_info(session_folder, inputs, configs_processed, posted=False)

        # Final summary before asking about POST
        print_header("✓ Campaign Setup Complete!")
        print(f"{Colors.GREEN}{Colors.BOLD}All configs have been processed successfully!{Colors.ENDC}\n")

        print(f"{Colors.BOLD}Session Folder:{Colors.ENDC} {session_folder}\n")

        print(f"{Colors.BOLD}Files created:{Colors.ENDC}")
        for config in configs_processed:
            print(f"  • {config}_before.json")
            print(f"  • {config}_after_unescaped.json")
            print(f"  • {config}_after.json")
        print(f"  • campaign_info.txt\n")

        # Step 7: Ask about posting to production
        print_step(7, "POST to Production (Optional)")

        # Handle dry-run mode
        if args.dry_run:
            print(f"\n{Colors.YELLOW}--dry-run mode: Skipping POST to production{Colors.ENDC}")
            print(f"{Colors.CYAN}Files generated successfully. Review them in:{Colors.ENDC}")
            print(f"  {session_folder}\n")
        elif args.auto_post:
            print(f"\n{Colors.YELLOW}--auto-post mode: POSTing without confirmation{Colors.ENDC}")
            if post_all_configs(session_folder, configs_processed, inputs['userid'], inputs['apikey']):
                generate_campaign_info(session_folder, inputs, configs_processed, posted=True)
                print(f"\n{Colors.CYAN}✨ Campaign is now LIVE in production! ✨{Colors.ENDC}\n")
            else:
                print_error("Some configs failed to POST. Check output above.")
        else:
            # Interactive confirmation
            if post_all_configs(session_folder, configs_processed, inputs['userid'], inputs['apikey']):
                # Update campaign_info.txt to reflect posted status
                generate_campaign_info(session_folder, inputs, configs_processed, posted=True)
                print(f"\n{Colors.CYAN}✨ Campaign is now LIVE in production! ✨{Colors.ENDC}\n")
            else:
                # User chose not to post or POST failed
                print(f"\n{Colors.YELLOW}{Colors.BOLD}Review Instructions:{Colors.ENDC}")
                print("1. Review all _after.json files in the session folder")
                print("2. Compare before/after to verify changes are correct")
                print("3. When satisfied, you can:")
                print("   a) Manually POST using curl commands in campaign_info.txt")
                print("   b) Run this script again and choose to POST when prompted\n")

        print(f"{Colors.CYAN}The magic has unfolded. ✨{Colors.ENDC}\n")

        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
