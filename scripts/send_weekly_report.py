"""
CLI script for generating and sending weekly engineering reports.
Reads report data from JSON, renders email, and sends via SendGrid.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from config.settings import settings
from data.models import WeeklyReport
from core.email_renderer import PlainTextEmailRenderer
from core.email_sender import EmailSender, EmailSendError
from utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()
app = typer.Typer()


@app.command()
def send_report(
    input_file: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to JSON file containing report data",
        exists=True
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print email without sending"
    ),
    recipients: Optional[str] = typer.Option(
        None,
        "--to",
        help="Override recipients (comma-separated emails)"
    )
):
    """
    Generate and send weekly engineering report email.
    
    Reads structured report data from JSON, validates it,
    renders to email format, and sends via SendGrid.
    """
    try:
        # Load and validate report data
        console.print(f"[blue]📂 Loading report from {input_file}[/blue]")
        report = load_report(input_file)
        
        # Render email
        console.print("[blue]✍️  Rendering email template[/blue]")
        renderer = PlainTextEmailRenderer()
        subject, body = renderer.render(report)
        
        # Display preview
        console.print("\n")
        console.print(Panel(
            f"[bold]{subject}[/bold]\n\n{body[:500]}...",
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
        
        console.print(f"\n[blue]📤 Sending to {len(to_emails)} recipients[/blue]")
        
        asyncio.run(send_email_async(to_emails, subject, body))
        
        console.print("[bold green]✓ Email sent successfully![/bold green]")
    
    except Exception as e:
        console.print(f"[bold red]✗ Error: {str(e)}[/bold red]")
        logger.exception("Failed to send weekly report")
        sys.exit(1)


def load_report(file_path: Path) -> WeeklyReport:
    """
    Load and validate report data from JSON file.
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Validated WeeklyReport instance
    
    Raises:
        ValueError: If JSON is invalid or fails validation
    """
    try:
        data = json.loads(file_path.read_text())
        return WeeklyReport(**data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}") from e
    except Exception as e:
        raise ValueError(f"Failed to parse report: {e}") from e


async def send_email_async(to_emails: list[str], subject: str, body: str):
    """Async wrapper for email sending."""
    sender = EmailSender()
    await sender.send_email(to_emails, subject, body)


if __name__ == "__main__":
    app()