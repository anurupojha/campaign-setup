#!/usr/bin/env python3
"""
Enhanced Terminal UI for Campaign Setup
Uses rich library for beautiful terminal experience
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Rich library imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.align import Align

# Import our existing logic
sys.path.insert(0, str(Path(__file__).parent))
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

console = Console()

def show_header():
    """Show beautiful header"""
    header = Panel.fit(
        "[bold cyan]Campaign Setup Wizard[/bold cyan]\n"
        "[dim]Simplified campaign configuration for streak campaigns[/dim]",
        border_style="cyan",
        padding=(1, 4)
    )
    console.print("\n")
    console.print(Align.center(header))
    console.print("\n")


def show_step_header(step_num, total_steps, title):
    """Show step progress"""
    progress_text = f"[bold cyan]Step {step_num}/{total_steps}:[/bold cyan] {title}"
    console.print(Panel(progress_text, border_style="cyan", box=box.ROUNDED))
    console.print()


def get_basic_details():
    """Collect basic campaign details"""
    show_step_header(1, 7, "Basic Campaign Details")

    inputs = {}

    # Campaign name
    inputs['campaign_name'] = Prompt.ask(
        "[cyan]Campaign Name[/cyan] (e.g., upi_streak_6)",
        default=""
    ).strip()

    while not inputs['campaign_name']:
        console.print("[red]✗ Campaign name cannot be empty[/red]")
        inputs['campaign_name'] = Prompt.ask(
            "[cyan]Campaign Name[/cyan]",
            default=""
        ).strip()

    console.print(f"[green]✓[/green] Campaign: {inputs['campaign_name']}")

    # Campaign ID (always provided by team)
    console.print("\n[dim]Campaign ID is provided by your team[/dim]")
    inputs['campaign_id'] = Prompt.ask("[cyan]Campaign ID (UUID from team)[/cyan]").strip()

    while not inputs['campaign_id']:
        console.print("[red]✗ Campaign ID cannot be empty[/red]")
        inputs['campaign_id'] = Prompt.ask("[cyan]Campaign ID[/cyan]").strip()

    console.print(f"[green]✓[/green] Campaign ID: [dim]{inputs['campaign_id']}[/dim]")

    # Campaign type
    console.print("\n[bold]Campaign Type:[/bold]")
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column(style="cyan", width=6)
    table.add_column()
    table.add_row("[1]", "UPI  - Both P2P + Scan & Pay eligible")
    table.add_row("[2]", "SNP  - Scan & Pay only")
    table.add_row("[3]", "P2P  - Peer-to-peer only")
    console.print(table)

    type_choice = IntPrompt.ask("[cyan]Select type[/cyan]", choices=["1", "2", "3"])
    type_map = {1: 'UPI', 2: 'SNP', 3: 'P2P'}
    inputs['campaign_type'] = type_map[type_choice]
    console.print(f"[green]✓[/green] Type: {inputs['campaign_type']}")

    # Duration and transactions
    console.print()
    inputs['duration_days'] = IntPrompt.ask("[cyan]Duration (days)[/cyan]", default=14)
    inputs['max_allowed'] = IntPrompt.ask("[cyan]Max Allowed (transactions)[/cyan]", default=5)

    console.print(f"[green]✓[/green] Duration: {inputs['duration_days']} days")
    console.print(f"[green]✓[/green] Max Transactions: {inputs['max_allowed']}")

    return inputs


def get_transaction_details(inputs):
    """Collect transaction details"""
    show_step_header(2, 7, "Transaction Details")

    inputs['min_txn_amount'] = IntPrompt.ask(
        "[cyan]Minimum Transaction Amount (Rs)[/cyan]",
        default=10
    )

    inputs['total_offer'] = IntPrompt.ask(
        f"[cyan]Total Campaign Offer (Rs)[/cyan] [dim](for {inputs['max_allowed']} payments)[/dim]",
        default=50
    )

    # Calculate per-transaction reward
    inputs['per_txn_reward'] = inputs['total_offer'] // inputs['max_allowed']

    console.print(f"\n[green]✓[/green] Min Transaction: Rs {inputs['min_txn_amount']}")
    console.print(f"[green]✓[/green] Total Offer: Rs {inputs['total_offer']}")
    console.print(f"[green]✓[/green] Per-Transaction: Rs {inputs['per_txn_reward']} [dim](auto-calculated)[/dim]")

    return inputs


def get_eligibility_details(inputs):
    """Collect eligibility details"""
    show_step_header(3, 7, "Additional Eligibility")

    inputs['is_rupay'] = Confirm.ask("[cyan]Is this a RuPay campaign?[/cyan]", default=False)
    inputs['is_bank_specific'] = Confirm.ask("[cyan]Is this bank-specific?[/cyan]", default=False)

    if inputs['is_bank_specific']:
        inputs['issuer_code'] = Prompt.ask("[cyan]Bank Issuer Code[/cyan]").strip()
    else:
        inputs['issuer_code'] = None

    console.print(f"\n[green]✓[/green] RuPay: {'Yes' if inputs['is_rupay'] else 'No'}")
    console.print(f"[green]✓[/green] Bank-Specific: {'Yes (' + inputs['issuer_code'] + ')' if inputs['is_bank_specific'] else 'No'}")

    return inputs


def select_banner(inputs):
    """Banner selection with table"""
    show_step_header(4, 7, "Banner Selection")

    # Load banner registry
    banner_registry = load_banner_registry()
    banners = banner_registry['banners']

    # Create table
    table = Table(title="Available Banners", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Callout", style="white")

    for banner in banners:
        table.add_row(f"[{banner['id']}]", banner['callout'])

    table.add_row("[0]", "[yellow]Enter custom banner[/yellow]")

    console.print(table)

    banner_choice = IntPrompt.ask(
        f"\n[cyan]Select banner[/cyan] [dim](Suggestion: look for 'Rs {inputs['total_offer']} on {inputs['max_allowed']} payments')[/dim]",
        choices=[str(i) for i in range(len(banners) + 1)]
    )

    if banner_choice == 0:
        # Custom banner
        inputs['banner_url'] = Prompt.ask("[cyan]Enter banner URL[/cyan]").strip()
        callout = Prompt.ask("[cyan]Enter callout description[/cyan] [dim](e.g., Rs 75 on 7 payments)[/dim]").strip()

        # Save to registry
        new_id = max([b['id'] for b in banners]) + 1
        new_banner = {"id": new_id, "callout": callout, "url": inputs['banner_url']}
        banners.append(new_banner)
        banner_registry['banners'] = banners

        registry_file = Path.home() / "documents" / "campaign_setup" / "banner_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(banner_registry, f, indent=2)

        console.print(f"[green]✓[/green] Saved new banner (will appear as option [{new_id}] next time)")
    else:
        selected = next(b for b in banners if b['id'] == banner_choice)
        inputs['banner_url'] = selected['url']
        console.print(f"[green]✓[/green] Selected: {selected['callout']}")

    return inputs


def select_subtitle(inputs):
    """Subtitle selection with table"""
    show_step_header(5, 7, "Bottom Sheet Subtitle")

    # Load subtitle templates
    subtitle_data = load_subtitle_templates()
    subtitles = subtitle_data['subtitles']

    # Create table
    table = Table(title="Available Subtitles", box=box.ROUNDED, title_style="bold cyan")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Text", style="white")

    for subtitle in subtitles:
        display_text = subtitle['text']
        if subtitle.get('has_placeholder'):
            display_text = display_text.replace('X', str(inputs['per_txn_reward']))
        table.add_row(f"[{subtitle['id']}]", display_text)

    table.add_row("[0]", "[yellow]Enter custom subtitle[/yellow]")

    console.print(table)

    subtitle_choice = IntPrompt.ask(
        "\n[cyan]Select subtitle[/cyan]",
        choices=[str(i) for i in range(len(subtitles) + 1)]
    )

    if subtitle_choice == 0:
        # Custom subtitle
        inputs['bottom_sheet_subtitle'] = Prompt.ask(
            "[cyan]Enter subtitle[/cyan] [dim](use \\\\n for line breaks)[/dim]"
        ).strip()

        # Save to templates
        new_id = max([s['id'] for s in subtitles]) + 1
        new_template = {
            "id": new_id,
            "text": inputs['bottom_sheet_subtitle'],
            "description": "Custom template"
        }
        subtitles.append(new_template)
        subtitle_data['subtitles'] = subtitles

        templates_file = Path.home() / "documents" / "campaign_setup" / "subtitle_templates.json"
        with open(templates_file, 'w') as f:
            json.dump(subtitle_data, f, indent=2)

        console.print(f"[green]✓[/green] Saved new subtitle (will appear as option [{new_id}] next time)")
    else:
        selected = next(s for s in subtitles if s['id'] == subtitle_choice)
        subtitle_text = selected['text']

        if selected.get('has_placeholder'):
            subtitle_text = subtitle_text.replace('X', str(inputs['per_txn_reward']))

        inputs['bottom_sheet_subtitle'] = subtitle_text
        console.print(f"[green]✓[/green] Selected: {subtitle_text}")

    return inputs


def load_api_credentials(inputs):
    """Load API credentials silently"""
    credentials = load_credentials()

    if credentials:
        inputs['userid'] = credentials['userid']
        inputs['apikey'] = credentials['apikey']
        console.print("[green]✓[/green] Using saved API credentials")
    else:
        console.print("[red]✗ No saved credentials found[/red]")
        console.print("Run the script in interactive mode first to save credentials")
        sys.exit(1)

    return inputs


def show_summary(inputs):
    """Show beautiful summary before processing"""
    show_step_header(6, 7, "Campaign Summary")

    # Create summary table
    table = Table(box=box.DOUBLE_EDGE, border_style="cyan", show_header=False)
    table.add_column("Field", style="cyan bold", width=25)
    table.add_column("Value", style="white")

    table.add_row("Campaign Name", inputs['campaign_name'])
    table.add_row("Campaign ID", f"[dim]{inputs['campaign_id']}[/dim]")
    table.add_row("Type", inputs['campaign_type'])
    table.add_row("Duration", f"{inputs['duration_days']} days")
    table.add_row("Max Transactions", str(inputs['max_allowed']))
    table.add_row("Total Offer", f"Rs {inputs['total_offer']}")
    table.add_row("Per-Transaction Reward", f"Rs {inputs['per_txn_reward']}")
    table.add_row("Min Transaction Amount", f"Rs {inputs['min_txn_amount']}")
    table.add_row("RuPay Campaign", "Yes" if inputs['is_rupay'] else "No")
    bank_specific = f"Yes ({inputs['issuer_code']})" if inputs['is_bank_specific'] else "No"
    table.add_row("Bank-Specific", bank_specific)
    table.add_row("Banner", f"[dim]{inputs['banner_url'].split('/')[-1]}[/dim]")
    table.add_row("Bottom Sheet", inputs['bottom_sheet_subtitle'][:50] + "...")

    console.print(table)
    console.print()

    # Determine configs needed
    configs_needed = determine_configs_needed(inputs['campaign_type'])

    console.print(f"[bold]Configs to be processed:[/bold] [cyan]{len(configs_needed)}[/cyan]")
    for i, config in enumerate(configs_needed, 1):
        console.print(f"  {i}. {config}")

    console.print()
    return Confirm.ask("[bold cyan]Proceed with campaign setup?[/bold cyan]", default=True)


def process_campaign(inputs):
    """Process all configs with progress indicators"""
    show_step_header(7, 7, "Processing Campaign")

    # Determine configs needed
    configs_needed = determine_configs_needed(inputs['campaign_type'])

    # Create session folder
    session_folder = create_session_folder(inputs['campaign_name'])
    console.print(f"[green]✓[/green] Created session folder: [dim]{session_folder}[/dim]\n")

    # Fetch configs with progress
    console.print("[bold]Fetching configs from API...[/bold]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for config in configs_needed:
            task = progress.add_task(f"Fetching {config}...", total=None)
            if fetch_config(config, session_folder, inputs['userid'], inputs['apikey']):
                progress.update(task, description=f"[green]✓ Fetched {config}[/green]")
            else:
                progress.update(task, description=f"[red]✗ Failed {config}[/red]")

    console.print()

    # Process configs with progress
    console.print("[bold]Processing configs...[/bold]")
    configs_processed = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        for config in configs_needed:
            task = progress.add_task(f"Processing {config}...", total=None)
            if process_config(config, session_folder, inputs):
                progress.update(task, description=f"[green]✓ Processed {config}[/green]")
                configs_processed.append(config)
            else:
                progress.update(task, description=f"[red]✗ Failed {config}[/red]")

    console.print()

    # Generate summary
    generate_campaign_info(session_folder, inputs, configs_processed, posted=False)
    console.print("[green]✓[/green] Generated campaign_info.txt\n")

    return session_folder, configs_processed


def show_completion(session_folder, configs_processed):
    """Show completion summary"""
    completion_panel = Panel(
        "[bold green]✨ Campaign Setup Complete! ✨[/bold green]\n\n"
        f"[cyan]Session Folder:[/cyan]\n{session_folder}\n\n"
        f"[cyan]Configs Processed:[/cyan] {len(configs_processed)}\n"
        "All files are ready for review",
        border_style="green",
        box=box.DOUBLE
    )
    console.print(completion_panel)
    console.print()


def update_retool_config(inputs):
    """Update Retool STREAK_JOURNEY_JOB_CONFIG with campaign details"""
    console.print("\n[bold cyan]Retool Configuration Update[/bold cyan]\n")

    # Initialize API and fetch config first
    console.print("[dim]Fetching existing campaigns...[/dim]")
    api = HeimdalJourneyConfigAPI(inputs['userid'], inputs['apikey'])

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Fetch config
        task = progress.add_task("Fetching config...", total=None)
        success, config_data, error = api.get_config()
        if not success:
            progress.update(task, description=f"[red]✗ Failed to fetch: {error}[/red]")
            console.print("[red]✗ Retool update failed[/red]\n")
            return False
        progress.update(task, description="[green]✓ Fetched config[/green]")

        # Parse value
        task = progress.add_task("Parsing config...", total=None)
        success, value_obj, error = parse_value_field(config_data)
        if not success:
            progress.update(task, description=f"[red]✗ Failed to parse: {error}[/red]")
            console.print("[red]✗ Retool update failed[/red]\n")
            return False
        progress.update(task, description="[green]✓ Parsed config[/green]")

    # Get list of existing campaigns
    batch_rules = value_obj.get('batch_assignment_rules', {}).get('configs', [])
    journey_rules = value_obj.get('journey_rules', {}).get('configs', [])
    existing_campaigns = set()
    for config in batch_rules + journey_rules:
        campaign_name = config.get('config_key')
        if campaign_name:
            existing_campaigns.add(campaign_name)

    console.print(f"\n[dim]Found {len(existing_campaigns)} existing campaigns in config[/dim]\n")

    # Ask if this is a chain campaign
    is_chain = Confirm.ask("[cyan]Is this a chain campaign?[/cyan]", default=False)

    if is_chain:
        # Validate next campaign exists
        while True:
            next_campaign = Prompt.ask(
                "[cyan]What is the next campaign?[/cyan] [dim](campaign_name user progresses to after completion)[/dim]"
            ).strip()

            # Special case: NA is always valid
            if next_campaign == "NA":
                console.print("[yellow]Note: NA means no progression (campaign ends here)[/yellow]")
                break

            # Check if campaign exists
            if next_campaign in existing_campaigns:
                console.print(f"[green]✓[/green] Found '{next_campaign}' in config")
                break
            else:
                console.print(f"[red]✗ Campaign '{next_campaign}' not found in config[/red]")
                console.print(f"[yellow]Available campaigns:[/yellow]")
                for i, camp in enumerate(sorted(existing_campaigns)[:10], 1):
                    console.print(f"  {i}. {camp}")
                if len(existing_campaigns) > 10:
                    console.print(f"  ... and {len(existing_campaigns) - 10} more")
                console.print()

                # Ask to continue or cancel
                if not Confirm.ask("[yellow]Try again?[/yellow]", default=True):
                    console.print("[dim]Retool update cancelled[/dim]\n")
                    return False
    else:
        next_campaign = "NA"

    console.print(f"[green]✓[/green] Next Campaign: {next_campaign}\n")

    # Continue with update
    console.print("[dim]Updating STREAK_JOURNEY_JOB_CONFIG...[/dim]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Check if campaign already exists
        task = progress.add_task("Checking for duplicates...", total=None)
        exists_in = check_campaign_exists(
            inputs['campaign_id'],
            inputs['campaign_name'],
            value_obj
        )

        locations = [k for k, v in exists_in.items() if v]
        if locations:
            progress.update(task, description=f"[yellow]⚠ Campaign already exists in {', '.join(locations)}[/yellow]")
            console.print(f"[yellow]⚠ Campaign already configured in Retool ({', '.join(locations)})[/yellow]\n")
            return True
        progress.update(task, description="[green]✓ No duplicates found[/green]")

        # Add campaign
        task = progress.add_task("Adding campaign...", total=None)
        modified_value_obj = add_campaign_to_config(
            inputs['campaign_name'],
            inputs['campaign_id'],
            next_campaign,
            value_obj
        )
        progress.update(task, description="[green]✓ Campaign added to config[/green]")

        # Update config
        task = progress.add_task("Posting to Retool...", total=None)
        config_data['value'] = json.dumps(modified_value_obj, indent=2)
        config_data['updated_by'] = f"campaign_setup_{inputs['campaign_name']}"

        success, message = api.update_config(config_data)
        if success:
            progress.update(task, description="[green]✓ Retool config updated[/green]")
            console.print("\n[bold green]✅ Retool configuration updated successfully![/bold green]\n")
            return True
        else:
            progress.update(task, description=f"[red]✗ Failed: {message}[/red]")
            console.print(f"[red]✗ Retool update failed: {message}[/red]\n")
            return False


def ask_about_posting(session_folder, configs_processed, inputs):
    """Ask about posting to production with double confirmation"""
    console.print("[bold yellow]POST to Production[/bold yellow]\n")

    console.print("[yellow]⚠  This will modify the LIVE production system[/yellow]")
    console.print(f"[yellow]⚠  {len(configs_processed)} configs will be posted[/yellow]\n")

    # First confirmation
    if not Confirm.ask("[bold]Do you want to POST these configs to production now?[/bold]", default=False):
        console.print("[dim]Skipped POST. Files are ready for manual review.[/dim]")
        return False

    console.print()
    console.print("[bold]The script will:[/bold]")
    console.print("  1. POST each config one by one")
    console.print("  2. Show success/failure for each")
    console.print("  3. Verify changes by fetching configs again")
    console.print("  4. Save verification files")
    console.print("  5. Update Retool dashboard configuration\n")

    # Second confirmation
    if not Confirm.ask("[bold red]Are you ABSOLUTELY SURE you want to proceed?[/bold red]", default=False):
        console.print("[dim]POST cancelled. Files are ready for manual review.[/dim]")
        return False

    # POST configs
    console.print()
    if post_all_configs(session_folder, configs_processed, inputs['userid'], inputs['apikey']):
        generate_campaign_info(session_folder, inputs, configs_processed, posted=True)
        console.print("\n[bold green]✨ Campaign configs posted successfully! ✨[/bold green]\n")

        # Update Retool config
        update_retool_config(inputs)

        console.print("\n[bold green]✨ Campaign is now LIVE in production! ✨[/bold green]\n")
        return True
    else:
        console.print("\n[yellow]Some configs failed to POST. Check output above.[/yellow]\n")
        return False


def main():
    """Main UI flow"""
    try:
        show_header()

        # Collect inputs
        inputs = get_basic_details()
        inputs = get_transaction_details(inputs)
        inputs = get_eligibility_details(inputs)
        inputs = select_banner(inputs)
        inputs = select_subtitle(inputs)
        inputs = load_api_credentials(inputs)

        # Show summary and confirm
        if not show_summary(inputs):
            console.print("[yellow]Campaign setup cancelled.[/yellow]")
            return 0

        # Process campaign
        session_folder, configs_processed = process_campaign(inputs)

        # Show completion
        show_completion(session_folder, configs_processed)

        # Ask about posting
        ask_about_posting(session_folder, configs_processed, inputs)

        console.print("[cyan]✨ Done! ✨[/cyan]\n")
        return 0

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Setup cancelled by user.[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
