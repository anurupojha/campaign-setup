#!/usr/bin/env python3
"""
Web UI for Campaign Setup using Streamlit
Access via localhost in your browser
"""

import sys
import streamlit as st
from pathlib import Path
import json

# Base directory for the app (works both locally and on Streamlit Cloud)
APP_DIR = Path(__file__).parent

# Import existing logic
sys.path.insert(0, str(APP_DIR))
from setup_campaign_master import (
    load_credentials, load_banner_registry, load_subtitle_templates,
    determine_configs_needed, create_session_folder,
    fetch_config, process_config, generate_campaign_info,
    post_all_configs
)
from retool_integration import (
    HeimdalJourneyConfigAPI, parse_value_field,
    add_campaign_to_config, check_campaign_exists
)

# Page configuration
st.set_page_config(
    page_title="Campaign Setup Wizard",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #00d4ff;
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(90deg, #1e3a5f 0%, #2a5298 100%);
        margin-bottom: 30px;
    }
    .step-header {
        background-color: #f0f8ff;
        padding: 10px;
        border-left: 4px solid #00d4ff;
        margin: 20px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0  # Start with login
if 'inputs' not in st.session_state:
    st.session_state.inputs = {}
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False


def show_header():
    """Display main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Campaign Setup Wizard</h1>
        <p>Simplified campaign configuration for streak campaigns</p>
    </div>
    """, unsafe_allow_html=True)


def step0_login():
    """Step 0: API Authentication"""
    st.markdown('<div class="step-header"><h3>🔐 API Credentials</h3></div>', unsafe_allow_html=True)

    st.info("Enter your internal API credentials to access the campaign management system.")

    # Try to load saved credentials first (for convenience)
    saved_userid = ""
    saved_apikey = ""
    try:
        credentials = load_credentials()
        if credentials:
            saved_userid = credentials.get('userid', '')
            saved_apikey = credentials.get('apikey', '')
            st.success("✓ Found saved credentials - pre-filled below. You can modify if needed.")
    except:
        pass

    userid = st.text_input(
        "User ID",
        value=saved_userid,
        placeholder="e.g., 96cc31b5-2f09-4b22-8f93-d6e46177a84d",
        help="Your internal API user ID (UUID format)"
    )

    apikey = st.text_input(
        "API Key",
        value=saved_apikey,
        type="password",
        placeholder="Your API key",
        help="Your internal API key for campaign management"
    )

    if st.button("Login & Continue →", key="login_btn"):
        if userid and apikey:
            # Store in session
            st.session_state.inputs['userid'] = userid
            st.session_state.inputs['apikey'] = apikey
            st.session_state.authenticated = True
            st.session_state.step = 1
            st.success("✓ Credentials saved for this session")
            st.rerun()
        else:
            st.error("Please enter both User ID and API Key")


def step1_basic_details():
    """Step 1: Basic Campaign Details"""
    st.markdown('<div class="step-header"><h3>📋 Step 1/7: Basic Campaign Details</h3></div>', unsafe_allow_html=True)

    campaign_name = st.text_input(
        "Campaign Name",
        placeholder="e.g., upi_streak_6",
        help="Enter a unique campaign name"
    )

    campaign_id = st.text_input(
        "Campaign ID (UUID from team)",
        placeholder="UUID provided by your team",
        help="Campaign ID is provided by your team"
    )

    campaign_type = st.selectbox(
        "Campaign Type",
        ["UPI - Both P2P + Scan & Pay eligible",
         "SNP - Scan & Pay only",
         "P2P - Peer-to-peer only"]
    )

    col1, col2 = st.columns(2)
    with col1:
        duration_days = st.number_input("Duration (days)", min_value=1, value=14)
    with col2:
        max_allowed = st.number_input("Max Allowed Transactions", min_value=1, value=5)

    if st.button("Next →", key="step1_next"):
        if campaign_name and campaign_id:
            # Map campaign type
            type_map = {
                "UPI - Both P2P + Scan & Pay eligible": "UPI",
                "SNP - Scan & Pay only": "SNP",
                "P2P - Peer-to-peer only": "P2P"
            }

            st.session_state.inputs.update({
                'campaign_name': campaign_name,
                'campaign_id': campaign_id,
                'campaign_type': type_map[campaign_type],
                'duration_days': int(duration_days),
                'max_allowed': int(max_allowed)
            })
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("Please fill in all required fields")


def step2_transaction_details():
    """Step 2: Transaction Details"""
    st.markdown('<div class="step-header"><h3>💰 Step 2/7: Transaction Details</h3></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        min_txn_amount = st.number_input("Minimum Transaction Amount (Rs)", min_value=1, value=10)
    with col2:
        total_offer = st.number_input(
            f"Total Campaign Offer (Rs)",
            min_value=1,
            value=50,
            help=f"For {st.session_state.inputs['max_allowed']} payments"
        )

    per_txn_reward = total_offer // st.session_state.inputs['max_allowed']
    st.info(f"📊 Per-Transaction Reward (auto-calculated): Rs {per_txn_reward}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key="step2_back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Next →", key="step2_next"):
            st.session_state.inputs.update({
                'min_txn_amount': int(min_txn_amount),
                'total_offer': int(total_offer),
                'per_txn_reward': int(per_txn_reward)
            })
            st.session_state.step = 3
            st.rerun()


def step3_eligibility_details():
    """Step 3: Eligibility Details"""
    st.markdown('<div class="step-header"><h3>✅ Step 3/7: Additional Eligibility</h3></div>', unsafe_allow_html=True)

    is_rupay = st.checkbox("Is this a RuPay campaign?", value=False)
    is_bank_specific = st.checkbox("Is this bank-specific?", value=False)

    issuer_code = None
    if is_bank_specific:
        issuer_code = st.text_input("Bank Issuer Code", placeholder="Enter issuer code")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key="step3_back"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Next →", key="step3_next"):
            if is_bank_specific and not issuer_code:
                st.error("Please enter the bank issuer code")
            else:
                st.session_state.inputs.update({
                    'is_rupay': is_rupay,
                    'is_bank_specific': is_bank_specific,
                    'issuer_code': issuer_code
                })
                st.session_state.step = 4
                st.rerun()


def step4_banner_selection():
    """Step 4: Banner Selection"""
    st.markdown('<div class="step-header"><h3>🎨 Step 4/7: Banner Selection</h3></div>', unsafe_allow_html=True)

    banner_registry = load_banner_registry()
    banners = banner_registry['banners']

    st.write(f"💡 Suggestion: Look for 'Rs {st.session_state.inputs['total_offer']} on {st.session_state.inputs['max_allowed']} payments'")

    # Create options
    banner_options = {f"{b['callout']}": b for b in banners}
    banner_options["🆕 Enter custom banner"] = None

    selected_banner = st.selectbox("Select Banner", list(banner_options.keys()))

    banner_url = None
    if selected_banner == "🆕 Enter custom banner":
        banner_url = st.text_input("Banner URL", placeholder="https://...")
        callout = st.text_input("Callout Description", placeholder="e.g., Rs 75 on 7 payments")

        if banner_url and callout:
            # Save to registry
            if st.button("Save Custom Banner", key="save_banner"):
                new_id = max([b['id'] for b in banners]) + 1
                new_banner = {"id": new_id, "callout": callout, "url": banner_url}
                banners.append(new_banner)
                banner_registry['banners'] = banners

                registry_file = APP_DIR / "banner_registry.json"
                with open(registry_file, 'w') as f:
                    json.dump(banner_registry, f, indent=2)

                st.success(f"✓ Saved new banner (will appear as option next time)")
    else:
        banner = banner_options[selected_banner]
        banner_url = banner['url']
        st.image(banner_url, caption=selected_banner, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key="step4_back"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Next →", key="step4_next"):
            if banner_url:
                st.session_state.inputs['banner_url'] = banner_url
                st.session_state.step = 5
                st.rerun()
            else:
                st.error("Please select or enter a banner")


def step5_subtitle_selection():
    """Step 5: Subtitle Selection"""
    st.markdown('<div class="step-header"><h3>📝 Step 5/7: Bottom Sheet Subtitle</h3></div>', unsafe_allow_html=True)

    subtitle_data = load_subtitle_templates()
    subtitles = subtitle_data['subtitles']

    # Create options with placeholder replacement
    subtitle_options = {}
    for s in subtitles:
        display_text = s['text']
        if s.get('has_placeholder'):
            display_text = display_text.replace('X', str(st.session_state.inputs['per_txn_reward']))
        subtitle_options[display_text] = s

    subtitle_options["🆕 Enter custom subtitle"] = None

    selected_subtitle = st.selectbox("Select Subtitle", list(subtitle_options.keys()))

    subtitle_text = None
    if selected_subtitle == "🆕 Enter custom subtitle":
        subtitle_text = st.text_area("Custom Subtitle", placeholder="Use \\n for line breaks")

        if subtitle_text:
            if st.button("Save Custom Subtitle", key="save_subtitle"):
                new_id = max([s['id'] for s in subtitles]) + 1
                new_template = {
                    "id": new_id,
                    "text": subtitle_text,
                    "description": "Custom template"
                }
                subtitles.append(new_template)
                subtitle_data['subtitles'] = subtitles

                templates_file = APP_DIR / "subtitle_templates.json"
                with open(templates_file, 'w') as f:
                    json.dump(subtitle_data, f, indent=2)

                st.success("✓ Saved new subtitle")
    else:
        subtitle_text = selected_subtitle

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key="step5_back"):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("Next →", key="step5_next"):
            if subtitle_text:
                st.session_state.inputs['bottom_sheet_subtitle'] = subtitle_text
                st.session_state.step = 6
                st.rerun()
            else:
                st.error("Please select or enter a subtitle")


def step6_summary():
    """Step 6: Campaign Summary"""
    st.markdown('<div class="step-header"><h3>📊 Step 6/7: Campaign Summary</h3></div>', unsafe_allow_html=True)

    inputs = st.session_state.inputs

    # Display summary in a nice table
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Campaign Details**")
        st.write(f"**Campaign Name:** {inputs['campaign_name']}")
        st.write(f"**Campaign ID:** `{inputs['campaign_id']}`")
        st.write(f"**Type:** {inputs['campaign_type']}")
        st.write(f"**Duration:** {inputs['duration_days']} days")
        st.write(f"**Max Transactions:** {inputs['max_allowed']}")

    with col2:
        st.markdown("**Financial Details**")
        st.write(f"**Total Offer:** Rs {inputs['total_offer']}")
        st.write(f"**Per-Transaction:** Rs {inputs['per_txn_reward']}")
        st.write(f"**Min Transaction:** Rs {inputs['min_txn_amount']}")
        st.write(f"**RuPay Campaign:** {'Yes' if inputs['is_rupay'] else 'No'}")
        bank_specific = f"Yes ({inputs['issuer_code']})" if inputs['is_bank_specific'] else "No"
        st.write(f"**Bank-Specific:** {bank_specific}")

    st.markdown("**Content**")
    st.write(f"**Banner:** {inputs['banner_url'].split('/')[-1]}")
    st.write(f"**Subtitle:** {inputs['bottom_sheet_subtitle'][:100]}...")

    # Show configs that will be processed
    configs_needed = determine_configs_needed(inputs['campaign_type'])
    st.info(f"**Configs to be processed:** {len(configs_needed)}")
    for i, config in enumerate(configs_needed, 1):
        st.write(f"{i}. {config}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key="step6_back"):
            st.session_state.step = 5
            st.rerun()
    with col2:
        if st.button("Process Campaign →", key="step6_next"):
            # Credentials already in session from login
            st.session_state.step = 7
            st.rerun()


def step7_processing():
    """Step 7: Process Campaign"""
    st.markdown('<div class="step-header"><h3>⚙️ Step 7/7: Processing Campaign</h3></div>', unsafe_allow_html=True)

    inputs = st.session_state.inputs
    configs_needed = determine_configs_needed(inputs['campaign_type'])

    # Create session folder
    try:
        session_folder = create_session_folder(inputs['campaign_name'])
        st.success(f"✓ Created session folder: `{session_folder}`")
    except Exception as e:
        st.error(f"✗ Failed to create session folder: {e}")
        return

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Fetch configs
    st.subheader("Fetching Configs")
    fetch_errors = []
    for i, config in enumerate(configs_needed):
        try:
            status_text.text(f"Fetching {config}...")
            if fetch_config(config, session_folder, inputs['userid'], inputs['apikey']):
                st.success(f"✓ Fetched {config}")
            else:
                st.error(f"✗ Failed {config}")
                fetch_errors.append(config)
        except Exception as e:
            st.error(f"✗ Failed {config}: {e}")
            fetch_errors.append(config)
        progress_bar.progress((i + 1) / (len(configs_needed) * 2))

    if fetch_errors:
        st.warning(f"⚠️ Failed to fetch {len(fetch_errors)} config(s). Continuing with available configs...")

    # Process configs
    st.subheader("Processing Configs")
    configs_processed = []
    for i, config in enumerate(configs_needed):
        if config in fetch_errors:
            st.warning(f"⊘ Skipping {config} (fetch failed)")
            progress_bar.progress((len(configs_needed) + i + 1) / (len(configs_needed) * 2))
            continue

        try:
            status_text.text(f"Processing {config}...")
            if process_config(config, session_folder, inputs):
                st.success(f"✓ Processed {config}")
                configs_processed.append(config)
            else:
                st.error(f"✗ Failed {config}")
        except Exception as e:
            st.error(f"✗ Failed {config}: {e}")
        progress_bar.progress((len(configs_needed) + i + 1) / (len(configs_needed) * 2))

    # Generate summary
    try:
        generate_campaign_info(session_folder, inputs, configs_processed, posted=False)
        st.success("✓ Generated campaign_info.txt")
    except Exception as e:
        st.error(f"✗ Failed to generate campaign_info.txt: {e}")

    status_text.empty()
    progress_bar.progress(1.0)

    # Show completion
    st.markdown('<div class="success-box"><h3>✨ Campaign Setup Complete! ✨</h3></div>', unsafe_allow_html=True)
    st.write(f"**Session Folder:** `{session_folder}`")
    st.write(f"**Configs Processed:** {len(configs_processed)}")
    st.write("All files are ready for review")

    # Post to production option
    st.markdown("---")
    st.markdown('<div class="warning-box"><h4>⚠️ POST to Production</h4></div>', unsafe_allow_html=True)
    st.warning(f"This will modify the LIVE production system. {len(configs_processed)} configs will be posted.")

    if st.button("🚀 POST to Production", key="post_production"):
        st.markdown("### Posting to Production...")
        if post_all_configs(session_folder, configs_processed, inputs['userid'], inputs['apikey']):
            generate_campaign_info(session_folder, inputs, configs_processed, posted=True)
            st.success("✨ Streak configs posted successfully! ✨")

            # Update Retool config
            st.markdown("### Updating Retool Dashboard...")

            # Initialize API and fetch existing campaigns
            api = HeimdalJourneyConfigAPI(inputs['userid'], inputs['apikey'])

            with st.spinner("Fetching existing campaigns..."):
                success, config_data, error = api.get_config()
                if not success:
                    st.error(f"Failed to fetch config: {error}")
                else:
                    success, value_obj, error = parse_value_field(config_data)
                    if not success:
                        st.error(f"Failed to parse config: {error}")
                    else:
                        # Get existing campaigns
                        batch_rules = value_obj.get('batch_assignment_rules', {}).get('configs', [])
                        journey_rules = value_obj.get('journey_rules', {}).get('configs', [])
                        existing_campaigns = set()
                        for config in batch_rules + journey_rules:
                            campaign_name = config.get('config_key')
                            if campaign_name:
                                existing_campaigns.add(campaign_name)

                        st.info(f"Found {len(existing_campaigns)} existing campaigns")

                        # Ask about chain
                        is_chain = st.checkbox("Is this a chain campaign?", key="is_chain")

                        next_campaign = "NA"
                        if is_chain:
                            next_campaign = st.text_input(
                                "Next campaign name (must exist in config)",
                                placeholder="e.g., snp_new_10x5_streak",
                                key="next_campaign"
                            )

                            # Validate
                            if next_campaign and next_campaign != "NA":
                                if next_campaign in existing_campaigns:
                                    st.success(f"✓ Found '{next_campaign}' in config")
                                else:
                                    st.error(f"✗ Campaign '{next_campaign}' not found in config")
                                    with st.expander("Show available campaigns"):
                                        for camp in sorted(existing_campaigns)[:20]:
                                            st.write(f"• {camp}")

                        if st.button("Update Retool Config", key="update_retool"):
                            # Check duplicates
                            exists_in = check_campaign_exists(
                                inputs['campaign_id'],
                                inputs['campaign_name'],
                                value_obj
                            )

                            locations = [k for k, v in exists_in.items() if v]
                            if locations:
                                st.warning(f"⚠ Campaign already exists in: {', '.join(locations)}")
                            else:
                                # Add campaign
                                with st.spinner("Adding campaign to config..."):
                                    modified_value_obj = add_campaign_to_config(
                                        inputs['campaign_name'],
                                        inputs['campaign_id'],
                                        next_campaign,
                                        value_obj
                                    )

                                    # Update config
                                    config_data['value'] = json.dumps(modified_value_obj, indent=2)
                                    config_data['updated_by'] = f"campaign_setup_{inputs['campaign_name']}"

                                    success, message = api.update_config(config_data)

                                    if success:
                                        st.success("✅ Retool configuration updated successfully!")
                                        st.balloons()
                                    else:
                                        st.error(f"✗ Retool update failed: {message}")
        else:
            st.warning("Some configs failed to POST. Check output above.")

    if st.button("🔄 Start New Campaign", key="restart"):
        st.session_state.step = 1
        st.session_state.inputs = {}
        st.rerun()


def main():
    """Main app entry point"""
    show_header()

    # Sidebar for navigation
    with st.sidebar:
        st.markdown("### 📍 Progress")

        # Show login status
        if st.session_state.step == 0:
            st.markdown("**→ 🔐 Login**")
        elif st.session_state.authenticated:
            st.markdown("✓ 🔐 Authenticated")

        if st.session_state.step > 0:
            st.markdown("---")
            steps = [
                "Basic Details",
                "Transaction Details",
                "Eligibility",
                "Banner Selection",
                "Subtitle Selection",
                "Summary",
                "Processing"
            ]

            for i, step_name in enumerate(steps, 1):
                if st.session_state.step == i:
                    st.markdown(f"**→ {i}. {step_name}**")
                elif st.session_state.step > i:
                    st.markdown(f"✓ {i}. {step_name}")
                else:
                    st.markdown(f"{i}. {step_name}")

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("Campaign Setup Wizard v2.0")
        st.markdown("Simplified configuration for streak campaigns")

    # Main content based on step
    if st.session_state.step == 0:
        step0_login()
    elif st.session_state.step == 1:
        step1_basic_details()
    elif st.session_state.step == 2:
        step2_transaction_details()
    elif st.session_state.step == 3:
        step3_eligibility_details()
    elif st.session_state.step == 4:
        step4_banner_selection()
    elif st.session_state.step == 5:
        step5_subtitle_selection()
    elif st.session_state.step == 6:
        step6_summary()
    elif st.session_state.step == 7:
        step7_processing()


if __name__ == "__main__":
    main()
# Trigger redeploy
