"""
Master CLI script for generating complete weekly engineering reports.
Combines project updates, AI summary, GitHub stats, and email delivery.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

import typer
from rich.console import Console
from rich.panel import Panel

from config.settings import settings
from data.models import WeeklyReport
from ai.summarizer import AISummarizer, AISummarizerError
from core.email_renderer import PlainTextEmailRenderer
from core.email_sender import EmailSender, EmailSendError
from core.github_collector import GitHubCollector, GitHubCollectorError
from utils.github_stats_formatter import GitHubStatsFormatter
from utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()
app = typer.Typer()


@app.command()
def generate(
    input_file: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to projects.json file",
        exists=True
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview email without sending"
    ),
    skip_ai: bool = typer.Option(
        False,
        "--skip-ai",
        help="Skip AI summary generation"
    ),
    skip_github: bool = typer.Option(
        False,
        "--skip-github",
        help="Skip GitHub stats collection"
    ),
    github_days: int = typer.Option(
        7,
        "--github-days",
        help="Days of GitHub history to collect"
    ),
    style: str = typer.Option(
        "executive",
        "--style",
        help="AI summary style: executive, casual, or detailed"
    ),
    recipients: Optional[str] = typer.Option(
        None,
        "--to",
        help="Override recipients (comma-separated)"
    )
):
    """
    Generate and send complete weekly engineering report.
    
    Workflow:
    1. Load project updates from JSON
    2. Generate AI summary (optional)
    3. Collect GitHub stats (optional)
    4. Render email with all sections
    5. Send via SendGrid (unless --dry-run)
    """
    try:
        # Load project report
        console.print(f"[blue]📂 Loading project data from {input_file}[/blue]")
        report = load_report(input_file)
        
        # Generate AI summary
        ai_intro = None
        if not skip_ai:
            console.print("[blue]🤖 Generating AI summary...[/blue]")
            ai_intro = asyncio.run(generate_ai_summary(report, style))
            console.print(Panel(
                ai_intro,
                title="🤖 AI Introduction",
                border_style="cyan"
            ))
        
        # Collect GitHub stats
        github_stats = None
        if not skip_github:
            console.print(f"[blue]📊 Collecting GitHub stats (last {github_days} days)...[/blue]")
            github_stats = collect_github_stats(github_days)
            if github_stats:
                console.print(f"[dim]  {github_stats}[/dim]")
        
        # Render email
        console.print("[blue]✍️  Rendering email...[/blue]")
        renderer = PlainTextEmailRenderer()
        subject, body = renderer.render(
            report,
            ai_intro=ai_intro,
            github_stats=github_stats
        )
        
        # Preview
        console.print("\n")
        console.print(Panel(
            f"[bold]{subject}[/bold]\n\n{body}",
            title="📧 Email Preview",
            border_style="green"
        ))
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - Email not sent[/yellow]")
            return
        
        # Send email
        to_emails = (
            [e.strip() for e in recipients.split(",")]
            if recipients
            else settings.get_recipients_list()
        )
        
        console.print(f"\n[blue]📤 Sending to {len(to_emails)} recipients...[/blue]")
        asyncio.run(send_email_async(to_emails, subject, body))
        
        console.print("[bold green]✓ Report sent successfully![/bold green]")
    
    except Exception as e:
        console.print(f"[bold red]✗ Error: {e}[/bold red]")
        logger.exception("Failed to generate weekly report")
        raise typer.Exit(code=1)


def load_report(file_path: Path) -> WeeklyReport:
    """Load and validate project report from JSON."""
    try:
        data = json.loads(file_path.read_text())
        return WeeklyReport(**data)
    except Exception as e:
        raise ValueError(f"Failed to load report: {e}") from e


async def generate_ai_summary(report: WeeklyReport, style: str) -> str:
    """Generate AI summary of the report."""
    try:
        summarizer = AISummarizer()
        return await summarizer.summarize_weekly_report(report, style=style)
    except AISummarizerError as e:
        logger.warning(f"AI summary failed: {e}")
        return "This week's engineering update (AI summary unavailable)"


def collect_github_stats(days: int) -> Optional[str]:
    """Collect and format GitHub activity stats."""
    try:
        # Collect GitHub data
        collector = GitHubCollector()
        
        until = datetime.utcnow()
        since = until - timedelta(days=days)
        
        github_report = collector.collect_activity(since=since, until=until)
        
        # Format as single-line summary
        formatter = GitHubStatsFormatter()
        return formatter.format_weekly_summary(github_report)
    
    except GitHubCollectorError as e:
        logger.warning(f"GitHub stats collection failed: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error collecting GitHub stats: {e}")
        return None


async def send_email_async(to_emails: list[str], subject: str, body: str):
    """Send email via SendGrid."""
    sender = EmailSender()
    await sender.send_email(to_emails, subject, body)


if __name__ == "__main__":
    app()