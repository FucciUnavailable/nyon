"""
Interactive CLI wizard for creating weekly project reports.
Walks you through questions and generates a valid projects.json file.
"""

from datetime import date, timedelta
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from data.models import WeeklyReport, ProjectUpdate, ProjectStatus
from utils.json_exporter import JSONExporter
from utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()
app = typer.Typer()


@app.command()
def create(
    output: Path = typer.Option(
        Path("projects.json"),
        "--output",
        "-o",
        help="Output file path"
    ),
    auto_dates: bool = typer.Option(
        True,
        "--auto-dates",
        help="Auto-fill this week's dates"
    )
):
    """
    Interactive wizard to create a weekly project report JSON file.
    
    Walks through questions about each project and generates
    a properly formatted projects.json file.
    """
    console.print(Panel(
        "[bold cyan]Weekly Project Report Generator[/bold cyan]\n\n"
        "Let's build your weekly report step by step!",
        border_style="cyan"
    ))
    
    try:
        # Get basic info
        console.print("\n[bold]📅 Report Details[/bold]")
        
        if auto_dates:
            # Default to current week (Monday to Friday)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())  # Monday
            week_end = week_start + timedelta(days=4)  # Friday
            console.print(f"Auto-detected week: {week_start} to {week_end}")
        else:
            week_start = date.fromisoformat(
                Prompt.ask("Week start date (YYYY-MM-DD)")
            )
            week_end = date.fromisoformat(
                Prompt.ask("Week end date (YYYY-MM-DD)")
            )
        
        lead_name = Prompt.ask("Your name", default="Sebastian Lee")
        team_name = Prompt.ask("Team name", default="Product Engineering")
        
        # Collect projects
        console.print("\n[bold]📋 Projects[/bold]")
        projects = collect_projects()
        
        # Overall summary
        console.print("\n[bold]📊 Overall Summary[/bold]")
        summary_bullets = collect_summary_bullets(projects)

        # Bugs/Tickets resolved
        console.print("\n[bold]🐛 Bugs & Tickets (Optional)[/bold]")
        bugs_fixed = int(Prompt.ask("Bugs fixed this week", default="0"))
        tickets_resolved = int(Prompt.ask("Tickets resolved this week", default="0"))
        tickets_open = int(Prompt.ask("Tickets still open", default="0"))
        features_shipped = int(Prompt.ask("Features shipped", default="0"))

        # Next milestone
        console.print("\n[bold]🎯 Next Milestone[/bold]")
        next_milestone = Prompt.ask("Milestone name", default="Sprint completion")
        milestone_date_str = Prompt.ask(
            "Milestone date (YYYY-MM-DD or leave empty)",
            default=""
        )
        next_milestone_date = (
            date.fromisoformat(milestone_date_str)
            if milestone_date_str
            else None
        )
        
        # Build report
        report = WeeklyReport(
            week_start=week_start,
            week_end=week_end,
            lead_name=lead_name,
            team_name=team_name,
            projects=projects,
            summary_bullets=summary_bullets,
            next_milestone=next_milestone,
            next_milestone_date=next_milestone_date,
            bugs_fixed=bugs_fixed,
            tickets_resolved=tickets_resolved,
            tickets_open=tickets_open,
            features_shipped=features_shipped
        )
        
        # Save to file
        exporter = JSONExporter()
        exporter.export(report, output)
        
        console.print(f"\n[bold green]✓ Report saved to {output}[/bold green]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(f"  python scripts/generate_weekly_report.py --input {output} --dry-run")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        raise typer.Exit(code=1)
    
    except Exception as e:
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        logger.exception("Failed to create report")
        raise typer.Exit(code=1)


def collect_projects() -> List[ProjectUpdate]:
    """Interactively collect project updates."""
    projects = []
    
    while True:
        console.print(f"\n[bold cyan]Project #{len(projects) + 1}[/bold cyan]")
        
        name = Prompt.ask("Project name")
        
        # Status selection
        console.print("\nStatus options:")
        console.print("  [green]1. on_track[/green] (🟢 On Track)")
        console.print("  [yellow]2. slight_delay[/yellow] (🟡 Slight Delay)")
        console.print("  [blue]3. ahead[/blue] (🔵 Ahead of Schedule)")
        console.print("  [red]4. at_risk[/red] (🔴 At Risk)")
        
        status_choice = Prompt.ask(
            "Select status",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        status_map = {
            "1": ProjectStatus.ON_TRACK,
            "2": ProjectStatus.SLIGHT_DELAY,
            "3": ProjectStatus.AHEAD,
            "4": ProjectStatus.AT_RISK
        }
        status = status_map[status_choice]
        
        status_text = Prompt.ask(
            "Status description (optional)",
            default=status.display_name()
        )
        
        completed = Prompt.ask("What was completed this week?", default="None")
        in_progress = Prompt.ask("What's in progress?", default="None")
        blockers = Prompt.ask("Any blockers?", default="None")
        next_week = Prompt.ask("Plans for next week?", default="TBD")

        # Optional: Progress and ETA
        console.print("\n[dim]Optional: Progress tracking[/dim]")
        progress_str = Prompt.ask("Progress % (0-100, or leave empty)", default="")
        progress_percent = int(progress_str) if progress_str else None

        eta_str = Prompt.ask("ETA date (YYYY-MM-DD, or leave empty)", default="")
        eta = date.fromisoformat(eta_str) if eta_str else None

        projects.append(ProjectUpdate(
            name=name,
            status=status,
            status_text=status_text,
            completed=completed,
            in_progress=in_progress,
            blockers=blockers,
            next_week=next_week,
            progress_percent=progress_percent,
            eta=eta
        ))
        
        if not Confirm.ask("\nAdd another project?", default=True):
            break
    
    return projects


def collect_summary_bullets(projects: List[ProjectUpdate]) -> List[str]:
    """Collect overall summary bullets."""
    # Auto-generate first bullet
    on_track = sum(
        1 for p in projects
        if p.status in [ProjectStatus.ON_TRACK, ProjectStatus.AHEAD]
    )
    auto_bullet = f"{on_track}/{len(projects)} projects on or ahead of schedule"
    
    console.print(f"\n[dim]Auto-generated: {auto_bullet}[/dim]")
    
    bullets = [auto_bullet]
    
    # Ask for additional bullets
    while True:
        bullet = Prompt.ask(
            "Add summary bullet (or press Enter to finish)",
            default=""
        )
        
        if not bullet:
            break
        
        bullets.append(bullet)
    
    return bullets


if __name__ == "__main__":
    app()