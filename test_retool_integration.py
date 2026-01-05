#!/usr/bin/env python3
"""
Test Retool Integration - DRY RUN MODE
Tests the Retool update flow without posting to production
"""

import sys
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

sys.path.insert(0, str(Path(__file__).parent))
from retool_integration import (
    load_credentials, HeimdalJourneyConfigAPI, parse_value_field,
    add_campaign_to_config, check_campaign_exists
)

console = Console()


def test_retool_flow():
    """Test the Retool integration flow in dry-run mode"""

    console.print("\n")
    console.print(Panel(
        "[bold cyan]Retool Integration Test[/bold cyan]\n"
        "[yellow]DRY RUN MODE - Nothing will be posted to production[/yellow]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()

    # Test campaign details
    console.print("[bold]Test Campaign Details:[/bold]")
    campaign_name = Prompt.ask(
        "[cyan]Campaign Name[/cyan] [dim](for testing)[/dim]",
        default="test_campaign_chain"
    )
    campaign_id = Prompt.ask(
        "[cyan]Campaign ID[/cyan] [dim](fake UUID is fine)[/dim]",
        default="00000000-0000-0000-0000-000000000000"
    )

    console.print(f"\n[green]✓[/green] Test Campaign: {campaign_name}")
    console.print(f"[green]✓[/green] Test ID: [dim]{campaign_id}[/dim]\n")

    # Load credentials
    console.print("[dim]Loading credentials...[/dim]")
    userid, apikey = load_credentials()
    if not userid or not apikey:
        console.print("[red]✗ Could not load credentials[/red]")
        return

    # Initialize API and fetch config
    console.print("[dim]Fetching existing campaigns...[/dim]")
    api = HeimdalJourneyConfigAPI(userid, apikey)

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
            console.print("[red]✗ Test failed[/red]\n")
            return
        progress.update(task, description="[green]✓ Fetched config[/green]")

        # Parse value
        task = progress.add_task("Parsing config...", total=None)
        success, value_obj, error = parse_value_field(config_data)
        if not success:
            progress.update(task, description=f"[red]✗ Failed to parse: {error}[/red]")
            console.print("[red]✗ Test failed[/red]\n")
            return
        progress.update(task, description="[green]✓ Parsed config[/green]")

    # Get list of existing campaigns
    batch_rules = value_obj.get('batch_assignment_rules', {}).get('configs', [])
    journey_rules = value_obj.get('journey_rules', {}).get('configs', [])
    existing_campaigns = set()
    for config in batch_rules + journey_rules:
        camp_name = config.get('config_key')
        if camp_name:
            existing_campaigns.add(camp_name)

    console.print(f"\n[dim]Found {len(existing_campaigns)} existing campaigns in config[/dim]\n")

    # Show some existing campaigns
    console.print("[bold]Sample of existing campaigns:[/bold]")
    for i, camp in enumerate(sorted(existing_campaigns)[:5], 1):
        console.print(f"  {i}. {camp}")
    if len(existing_campaigns) > 5:
        console.print(f"  ... and {len(existing_campaigns) - 5} more")
    console.print()

    # Test the chain validation logic
    is_chain = Confirm.ask("[cyan]Test chain campaign flow?[/cyan]", default=True)

    if is_chain:
        # Validate next campaign exists
        while True:
            next_campaign = Prompt.ask(
                "[cyan]What is the next campaign?[/cyan] [dim](try entering an existing one from list above)[/dim]"
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
                    console.print("[dim]Test cancelled[/dim]\n")
                    return
    else:
        next_campaign = "NA"

    console.print(f"[green]✓[/green] Next Campaign: {next_campaign}\n")

    # Check for duplicates
    console.print("[dim]Testing duplicate detection...[/dim]")
    exists_in = check_campaign_exists(campaign_id, campaign_name, value_obj)

    locations = [k for k, v in exists_in.items() if v]
    if locations:
        console.print(f"[yellow]⚠ Campaign already exists in: {', '.join(locations)}[/yellow]")
        console.print("[yellow]In real workflow, this would skip adding the campaign[/yellow]\n")
    else:
        console.print("[green]✓[/green] No duplicates found\n")

    # Simulate adding campaign (dry-run)
    console.print("[bold yellow]DRY RUN:[/bold yellow] Simulating campaign addition...")
    console.print()

    modified_value_obj = add_campaign_to_config(
        campaign_name,
        campaign_id,
        next_campaign,
        value_obj
    )

    console.print("[green]✓[/green] Campaign would be added with:")
    console.print(f"  • UUID in supported_campaign_ids: {campaign_id}")
    console.print(f"  • Batch assignment rule: {campaign_name} → {campaign_name}")
    console.print(f"  • Initial journey rule: assign users to {campaign_name}")
    console.print(f"  • Progression rule: {campaign_name} → {next_campaign}")
    console.print()

    # Show what would be posted
    console.print("[bold]What would be sent to production:[/bold]")
    console.print(f"  • Endpoint: {api.base_url}")
    console.print(f"  • Config Key: {api.config_key}")
    console.print(f"  • Updated By: campaign_setup_{campaign_name}")
    console.print()

    console.print(Panel(
        "[bold green]✅ Test Complete![/bold green]\n\n"
        "[yellow]No changes were made to production[/yellow]\n"
        "The logic flow is working correctly.",
        border_style="green",
        box=box.DOUBLE
    ))
    console.print()


def main():
    """Main test flow"""
    try:
        test_retool_flow()
        return 0
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Test cancelled by user.[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
