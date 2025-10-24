"""
Email template rendering for weekly engineering reports.
Converts structured data into formatted email content with optional AI intro.
"""

from typing import Protocol, Optional
from data.models import WeeklyReport, ProjectUpdate
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailRenderer(Protocol):
    """Protocol for email renderers (allows dependency injection)."""

    def render(
        self,
        report: WeeklyReport,
        ai_intro: Optional[str] = None,
        github_stats: Optional[str] = None,
    ) -> tuple[str, str]:
        """Render report to (subject, body) tuple."""
        ...


class PlainTextEmailRenderer:
    """Renders weekly reports as plain text emails."""

    def __init__(self, include_emoji: bool = True):
        """
        Initialize renderer.

        Args:
            include_emoji: Whether to include status emojis in output
        """
        self.include_emoji = include_emoji

    def render(
        self,
        report: WeeklyReport,
        ai_intro: Optional[str] = None,
        github_stats: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Render a weekly report to plain text email format.

        Args:
            report: Validated weekly report data
            ai_intro: Optional AI-generated introduction (2-3 lines)
            github_stats: Optional GitHub activity summary footer

        Returns:
            Tuple of (subject, body) strings
        """
        subject = self._render_subject(report)
        body = self._render_body(report, ai_intro, github_stats)

        logger.info(f"Rendered email for {len(report.projects)} projects")
        return subject, body

    def _render_subject(self, report: WeeklyReport) -> str:
        """Generate email subject line."""
        return (
            f"Weekly Engineering Progress – "
            f"{report.week_start.isoformat()}–{report.week_end.isoformat()} "
            f"({report.get_project_list_str()})"
        )

    def _render_body(
        self, report: WeeklyReport, ai_intro: Optional[str], github_stats: Optional[str]
    ) -> str:
        """Generate email body."""
        parts = []

        # Add AI intro if provided
        if ai_intro:
            parts.append(f"🤖 {ai_intro}")
            parts.append("---")

        # Standard sections
        parts.extend(
            [
                self._render_header(report),
                self._render_projects(report),
                self._render_summary(report),
            ]
        )

        # Add GitHub stats footer if provided
        if github_stats:
            parts.append("---")
            parts.append(github_stats)

        # Footer signature
        parts.append(self._render_footer(report))

        return "\n\n".join(parts)

    def _render_header(self, report: WeeklyReport) -> str:
        """Render email header."""
        return (
            f"Greetings Everyone,\n\n"
            f"Here's a summary of this week's progress across active projects:"
        )

    def _render_projects(self, report: WeeklyReport) -> str:
        """Render all project blocks."""
        blocks = []
        for idx, project in enumerate(report.projects, start=1):
            blocks.append(self._render_project(idx, project))
        return "\n\n".join(blocks)

    def _render_project(self, index: int, project: ProjectUpdate) -> str:
        """Render a single project block."""
        status_emoji = project.status.emoji() if self.include_emoji else ""
        status_display = project.status_text or project.status.display_name()

        return (
            f"### {index}. {project.name}\n"
            f"Status: {status_emoji} {status_display}\n"
            f"Progress:\n"
            f"- Completed: {project.completed}\n"
            f"- In Progress: {project.in_progress}\n"
            f"- Blockers: {project.blockers}\n"
            f"Next Week:\n"
            f"- {project.next_week}"
        )

    def _render_summary(
        self, report: WeeklyReport, github_stats: Optional[str] = None
    ) -> str:
        """Render overall summary section with optional GitHub stats."""
        bullets = "\n".join([f"- {bullet}" for bullet in report.summary_bullets])

        # Add GitHub stats as final bullet if provided
        if github_stats:
            bullets += f"\n- 💻 {github_stats}"

        milestone_date = (
            report.next_milestone_date.isoformat()
            if report.next_milestone_date
            else "TBD"
        )

        return (
            f"Overall Summary:\n{bullets}\n\n"
            f"Next Milestone:\n"
            f"- {report.next_milestone} — {milestone_date}"
        )

    def _render_body(
        self, report: WeeklyReport, ai_intro: Optional[str], github_stats: Optional[str]
    ) -> str:
        """Generate email body."""
        parts = []

        # Add AI intro if provided
        if ai_intro:
            parts.append(f"🤖 {ai_intro}")
            parts.append("---")

        # Standard sections (pass github_stats to summary)
        parts.extend(
            [
                self._render_header(report),
                self._render_projects(report),
                self._render_summary(report, github_stats),  # <-- Pass it here
            ]
        )

        # Footer signature
        parts.append(self._render_footer(report))

        return "\n\n".join(parts)

    def _render_footer(self, report: WeeklyReport) -> str:
        """Render email signature."""
        return f"Best,\n{report.lead_name}\nSoftware Engineer\n({report.team_name})"


if __name__ == "__main__":
    # Example usage
    from datetime import date
    from data.models import ProjectStatus
    from rich import print as rprint

    report = WeeklyReport(
        week_start=date(2025, 10, 6),
        week_end=date(2025, 10, 11),
        lead_name="Sebastian Lee",
        projects=[
            ProjectUpdate(
                name="API Platform",
                status=ProjectStatus.ON_TRACK,
                completed="Auth refactor",
                in_progress="Pagination",
                blockers="None",
                next_week="Deploy to staging",
            )
        ],
        summary_bullets=["All projects on track"],
        next_milestone="Sprint 15",
        next_milestone_date=date(2025, 10, 18),
    )

    renderer = PlainTextEmailRenderer()

    # With AI intro
    ai_intro = (
        "Hi there! This is Claude, Amine's AI assistant. "
        "This week showed solid progress with our API Platform hitting all milestones. "
        "No major blockers — we're on track for Sprint 15!"
    )

    subject, body = renderer.render(report, ai_intro=ai_intro)

    rprint(f"[bold]SUBJECT:[/bold] {subject}\n")
    rprint(body)
