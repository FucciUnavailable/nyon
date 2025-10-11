"""
CLI script for collecting GitHub activity data.
Fetches PRs, commits, and issues, then exports to JSON.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from config.settings import settings
from core.github_collector import GitHubCollector, GitHubCollectorError
from utils.json_exporter import JSONExporter
from utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()
app = typer.Typer()


@app.command()
def collect(
    days: int = typer.Option(
        7,
        "--days",
        "-d",
        help="Number of days of history to collect"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output JSON file path (default: reports/github_activity_YYYY-MM-DD.json)"
    ),
    repos: Optional[str] = typer.Option(
        None,
        "--repos",
        help="Override repos (comma-separated, e.g. owner/repo1,owner/repo2)"
    )
):
    """
    Collect GitHub activity data from configured repositories.
    
    Fetches pull requests, commits, and open issues within the specified
    date range and exports to a structured JSON file.
    """
    try:
        console.print(f"[blue]🔍 Collecting GitHub activity from last {days} days[/blue]")
        
        # Date range
        until = datetime.utcnow()
        since = until - timedelta(days=days)
        
        # Initialize collector
        repo_list = (
            [r.strip() for r in repos.split(",")]
            if repos
            else None
        )
        collector = GitHubCollector(repos=repo_list)
        
        # Collect data
        report = collector.collect_activity(since=since, until=until)
        
        # Display summary table
        display_summary(report)
        
        # Export to JSON
        if output is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            output = settings.report_output_dir / f"github_activity_{date_str}.json"
        
        exporter = JSONExporter()
        exporter.export(report, output)
        
        console.print(f"\n[bold green]✓ Data collected and exported to {output}[/bold green]")
    
    except GitHubCollectorError as e:
        console.print(f"[bold red]✗ Collection failed: {e}[/bold red]")
        raise typer.Exit(code=1)
    
    except Exception as e:
        console.print(f"[bold red]✗ Unexpected error: {e}[/bold red]")
        logger.exception("Failed to collect GitHub data")
        raise typer.Exit(code=1)


def display_summary(report):
    """Display activity summary in a rich table."""
    table = Table(title="📊 GitHub Activity Summary")
    
    table.add_column("Repository", style="cyan", no_wrap=True)
    table.add_column("PRs", justify="right", style="green")
    table.add_column("Merged", justify="right", style="blue")
    table.add_column("Commits", justify="right", style="yellow")
    table.add_column("Open Issues", justify="right", style="red")
    table.add_column("Contributors", justify="right")
    
    for repo in report.repositories:
        table.add_row(
            repo.repo_name,
            str(repo.total_prs),
            str(repo.merged_prs),
            str(repo.total_commits),
            str(repo.total_open_issues),
            str(len(repo.unique_contributors))
        )
    
    # Add totals row
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{report.total_prs_across_repos}[/bold]",
        "-",
        f"[bold]{report.total_commits_across_repos}[/bold]",
        f"[bold]{report.total_open_issues_across_repos}[/bold]",
        "-",
        style="bold"
    )
    
    console.print("\n")
    console.print(table)


if __name__ == "__main__":
    app()