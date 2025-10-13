#!/usr/bin/env python3
"""
Simple workflow script for generating weekly reports.
This bypasses the typer CLI bug and provides an intuitive interface.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scripts.generate_weekly_report import generate
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def main():
    """Main workflow for creating and sending weekly reports."""

    console.print("\n[bold cyan]📊 Weekly Report Generator[/bold cyan]\n")

    # Step 1: Choose or create projects.json
    console.print("[yellow]Step 1: Project Data[/yellow]")

    # Check for existing projects.json
    if Path("projects.json").exists():
        use_existing = Confirm.ask(
            "Found existing projects.json. Use it?",
            default=True
        )
        if use_existing:
            input_file = Path("projects.json")
        else:
            console.print("\n[blue]Run this command to create a new one:[/blue]")
            console.print("  python scripts/create_projects_json.py\n")
            return
    else:
        console.print("[red]No projects.json found![/red]")
        console.print("\n[blue]Run this command to create one:[/blue]")
        console.print("  python scripts/create_projects_json.py\n")
        return

    # Step 2: Preview or send?
    console.print("\n[yellow]Step 2: Preview or Send?[/yellow]")
    action = Prompt.ask(
        "What would you like to do?",
        choices=["preview", "send"],
        default="preview"
    )

    dry_run = (action == "preview")

    # Step 3: Configure options
    console.print("\n[yellow]Step 3: Options[/yellow]")

    skip_ai = not Confirm.ask("Include AI summary?", default=True)
    skip_github = not Confirm.ask("Include GitHub stats?", default=False)

    style = "executive"
    if not skip_ai:
        style = Prompt.ask(
            "AI summary style",
            choices=["executive", "casual", "detailed"],
            default="executive"
        )

    # Step 4: Archive old report if sending
    if not dry_run and Path("projects.json").exists():
        archive = Confirm.ask(
            "Archive this report to weekly_logs/?",
            default=True
        )
        if archive:
            # Create archive directory
            archive_dir = Path("weekly_logs")
            archive_dir.mkdir(exist_ok=True)

            # Generate filename from dates in json
            import json
            data = json.loads(Path("projects.json").read_text())
            week_start = data.get("week_start", datetime.now().strftime("%Y-%m-%d"))
            archive_file = archive_dir / f"report_{week_start}.json"

            # Copy to archive
            Path("projects.json").rename(archive_file)
            console.print(f"[green]✓ Archived to {archive_file}[/green]")

            # Recreate the file for processing
            import shutil
            shutil.copy(archive_file, "projects.json")

    # Step 5: Generate and send
    console.print("\n[bold green]Generating report...[/bold green]\n")

    try:
        generate(
            input_file=input_file,
            dry_run=dry_run,
            skip_ai=skip_ai,
            skip_github=skip_github,
            github_days=7,
            style=style,
            recipients=None
        )
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        sys.exit(1)

    # Step 6: Next steps
    if dry_run:
        console.print("\n[yellow]To send the report, run this again and choose 'send'[/yellow]")
    else:
        console.print("\n[bold green]✓ Report sent successfully![/bold green]")
        console.print("\n[blue]Next steps:[/blue]")
        console.print("  1. Check your email")
        console.print("  2. Create next week's report with: python scripts/create_projects_json.py")


if __name__ == "__main__":
    main()
