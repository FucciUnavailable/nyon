"""
HTML email template rendering for weekly engineering reports.
Creates clean, professional HTML emails with minimal design.
"""

from typing import Optional
from data.models import WeeklyReport, ProjectUpdate, ProjectStatus
from utils.logger import setup_logger

logger = setup_logger(__name__)


class HTMLEmailRenderer:
    """Renders weekly reports as clean, professional HTML emails."""

    def __init__(self):
        """Initialize HTML renderer."""
        pass

    def render(
        self,
        report: WeeklyReport,
        ai_intro: Optional[str] = None,
        github_stats: Optional[str] = None,
    ) -> tuple[str, str, str]:
        """
        Render a weekly report to HTML email format.

        Args:
            report: Validated weekly report data
            ai_intro: Optional AI-generated introduction (2-3 lines)
            github_stats: Optional GitHub activity summary

        Returns:
            Tuple of (subject, html_body, plain_text_fallback)
        """
        subject = self._render_subject(report)
        html_body = self._render_html_body(report, ai_intro, github_stats)
        plain_text = self._render_plain_text_fallback(report, ai_intro, github_stats)

        logger.info(f"Rendered HTML email for {len(report.projects)} projects")
        return subject, html_body, plain_text

    def _render_subject(self, report: WeeklyReport) -> str:
        """Generate email subject line."""
        return (
            f"Weekly Engineering Update – "
            f"{report.week_start.strftime('%b %d')}–{report.week_end.strftime('%b %d, %Y')}"
        )

    def _render_html_body(
        self, report: WeeklyReport, ai_intro: Optional[str], github_stats: Optional[str]
    ) -> str:
        """Generate HTML email body."""

        # Build AI intro section
        ai_section = ""
        if ai_intro:
            ai_section = f"""
            <div style="margin: 0 0 24px 0;
                        padding: 18px 20px;
                        background-color: #f8f9fa;
                        border-left: 3px solid #7c3aed;
                        border-radius: 4px;">
                <div style="font-size: 13px;
                            font-weight: 600;
                            color: #7c3aed;
                            margin: 0 0 10px 0;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;">
                    🤖 AI Summary
                </div>
                <div style="font-size: 15px;
                            line-height: 1.6;
                            color: #202124;">
                    {ai_intro}
                </div>
            </div>
            """

        # Build project sections
        projects_html = "\n".join(
            [
                self._render_project(idx, project)
                for idx, project in enumerate(report.projects, start=1)
            ]
        )

        # Build bugs/tickets section if exists
        bugs_section = ""
        if (
            hasattr(report, "bugs_fixed")
            or hasattr(report, "tickets_resolved")
            or hasattr(report, "features_shipped")
        ):
            bugs_fixed = getattr(report, "bugs_fixed", 0)
            tickets_resolved = getattr(report, "tickets_resolved", 0)
            tickets_open = getattr(report, "tickets_open", 0)
            features_shipped = getattr(report, "features_shipped", 0)

            if (
                bugs_fixed > 0
                or tickets_resolved > 0
                or features_shipped > 0
                or tickets_open > 0
            ):
                parts = []
                if tickets_resolved > 0 or tickets_open > 0:
                    total_tickets = tickets_resolved + tickets_open
                    parts.append(f"{tickets_resolved}/{total_tickets} tickets resolved")
                if bugs_fixed > 0:
                    parts.append(f"{bugs_fixed} bugs fixed")
                if features_shipped > 0:
                    parts.append(f"{features_shipped} features shipped")

                bugs_text = ", ".join(parts)

                # Build ticket progress bar if we have ticket data
                ticket_graph = ""
                if tickets_resolved > 0 or tickets_open > 0:
                    total_tickets = tickets_resolved + tickets_open
                    resolved_pct = (
                        int((tickets_resolved / total_tickets) * 100)
                        if total_tickets > 0
                        else 0
                    )
                    open_pct = 100 - resolved_pct

                    ticket_graph = f"""
                    <table cellpadding="0" cellspacing="0" border="0" style="width: 100%; margin: 12px 0 0 0;">
                        <tr>
                            <td width="{resolved_pct}%" style="background-color: #34a853; height: 20px; border-radius: 4px 0 0 4px; font-size: 1px; line-height: 1px;">&nbsp;</td>
                            <td width="{open_pct}%" style="background-color: #fbbc04; height: 20px; border-radius: 0 4px 4px 0; font-size: 1px; line-height: 1px;">&nbsp;</td>
                        </tr>
                    </table>
                    <div style="font-size: 12px; color: #5f6368; margin: 4px 0 0 0;">
                        <span style="color: #34a853;">●</span> {tickets_resolved} resolved &nbsp;&nbsp;
                        <span style="color: #fbbc04;">●</span> {tickets_open} open
                    </div>
                    """

                bugs_section = f"""
                <div style="margin: 32px 0 0 0; padding: 16px 0; border-top: 1px solid #e8eaed;">
                    <div style="font-size: 14px; font-weight: 600; color: #5f6368; margin: 0 0 8px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                        🐛 Bugs Fixed & Issues Resolved
                    </div>
                    <div style="font-size: 15px; color: #202124; margin: 0 0 4px 0;">
                        {bugs_text}
                    </div>
                    {ticket_graph}
                </div>
                """

        # Build summary bullets
        summary_html = "\n".join(
            [
                f'<div style="margin: 0 0 6px 0; color: #202124;">• {bullet}</div>'
                for bullet in report.summary_bullets
            ]
        )

        # Build GitHub stats if exists
        github_section = ""
        if github_stats:
            github_section = f'<div style="margin: 6px 0 0 0; color: #202124;">• {github_stats}</div>'

        # Build milestone
        milestone_date = (
            report.next_milestone_date.strftime("%b %d, %Y")
            if report.next_milestone_date
            else "TBD"
        )

        # Generate simple progress chart
        on_track = report.get_on_track_count()
        total = report.get_total_count()
        chart_html = self._render_progress_chart(on_track, total)

        # Full HTML template - CLEAN AND MINIMAL
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Engineering Update</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #ffffff; color: #202124;">

    <!-- Main Container -->
    <div style="max-width: 680px; margin: 0 auto; padding: 40px 20px;">

        <!-- Header -->
        <div style="margin: 0 0 32px 0; padding: 0 0 24px 0; border-bottom: 2px solid #e8eaed;">
            <h1 style="margin: 0 0 8px 0; font-size: 24px; font-weight: 600; color: #202124; letter-spacing: -0.3px;">
                Weekly Engineering Update
            </h1>
            <div style="font-size: 14px; color: #5f6368;">
                {report.week_start.strftime("%B %d")} – {report.week_end.strftime("%B %d, %Y")}
            </div>
        </div>

        <!-- AI Intro -->
        {ai_section}

        <!-- Greeting -->
        <div style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.6; color: #202124; border-bottom: 2px solid #e8eaed;">
            Greetings Everyone,<br><br>
            Here's this week's progress across active projects:
        </div>

        <!-- Projects -->
        {projects_html}

        <!-- Bugs/Tickets Section -->
        {bugs_section}

        <!-- Overall Summary -->
        <div style="margin: 32px 0 0 0; padding: 16px 0; border-top: 1px solid #e8eaed;">
            <div style="font-size: 14px; font-weight: 600; color: #5f6368; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                Overall Summary
            </div>
            <div style="font-size: 15px; line-height: 1.7;">
                {summary_html}
                {github_section}
            </div>
        </div>

        <!-- Progress Chart -->
        {chart_html}

        <!-- Next Milestone -->
        <div style="margin: 24px 0 0 0; padding: 16px 0;">
            <div style="font-size: 14px; font-weight: 600; color: #5f6368; margin: 0 0 8px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                Next Milestone
            </div>
            <div style="font-size: 15px; color: #202124;">
                {report.next_milestone} — {milestone_date}
            </div>
        </div>

        <!-- Footer -->
        <div style="margin: 40px 0 0 0; padding: 24px 0 0 0; border-top: 1px solid #e8eaed; font-size: 15px; color: #202124;">
            <div style="margin: 0 0 4px 0;">Best,</div>
            <div style="margin: 0 0 2px 0; font-weight: 500;">{report.lead_name}</div>
            <div style="font-size: 14px; color: #5f6368;">Software Engineer</div>
            <div style="font-size: 14px; color: #5f6368;">{report.team_name}</div>
        </div>

    </div>

</body>
</html>
        """

        return html.strip()

    def _render_project(self, index: int, project: ProjectUpdate) -> str:
        """Render a single project in clean, minimal style."""
        status_display = project.status_text or project.status.display_name()
        status_emoji = project.status.emoji()
        status_color = self._get_status_color(project.status)

        return f"""
        <!-- Project {index} -->
        <div style="margin: 0 0 32px 0;">
            <div style="display: table; width: 100%; margin: 0 0 12px 0;">
                <div style="display: table-cell; vertical-align: middle;">
                    <h2 style="margin: 0; font-size: 18px; font-weight: 600; color: #202124;">
                        {index}. {project.name}    {status_emoji}
                    </h2>
                </div>
                <div style="display: table-cell; vertical-align: middle; text-align: right; white-space: nowrap; padding-left: 16px;">
                    <span style="display: inline-block;
                                  padding: 4px 10px;
                                  background-color: {self._get_status_bg(project.status)};
                                  border-radius: 12px;
                                  font-size: 13px;
                                  font-weight: 700;
                                  color: {status_color};">
                        {status_emoji} {status_display}
                    </span>
                </div>
            </div>

            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr>
                    <td style="padding: 8px 12px 8px 0; vertical-align: top; width: 100px; color: #5f6368; font-weight: 500;">
                        ✅<b>Completed </b>
                    </td>
                    <td style="padding: 8px 0; vertical-align: top; color: #202124; line-height: 1.5;">
                        {project.completed}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px 8px 0; vertical-align: top; color: #5f6368; font-weight: 500;">
                       🚧<b> In Progress </b>
                    </td>
                    <td style="padding: 8px 0; vertical-align: top; color: #202124; line-height: 1.5;">
                        {project.in_progress}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px 8px 0; vertical-align: top; color: #5f6368; font-weight: 500;">
                        🧱<b>Blockers</b> 
                    </td>
                    <td style="padding: 8px 0; vertical-align: top; color: #202124; line-height: 1.5;">
                        {project.blockers}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 12px 8px 0; vertical-align: top; color: #5f6368; font-weight: 500;">
                        🎯<b>Next Week</b> 
                    </td>
                    <td style="padding: 8px 0; vertical-align: top; color: #202124; line-height: 1.5;">
                        {project.next_week}
                    </td>
                </tr>
            </table>
        </div>
        """

    def _get_status_color(self, status: ProjectStatus) -> str:
        """Get text color for project status."""
        return {
            ProjectStatus.ON_TRACK: "#15803d",  # Dark green
            ProjectStatus.AHEAD: "#1e40af",  # Dark blue
            ProjectStatus.SLIGHT_DELAY: "#b45309",  # Dark amber
            ProjectStatus.AT_RISK: "#b91c1c",  # Dark red
        }[status]

    def _get_status_bg(self, status: ProjectStatus) -> str:
        """Get background color for project status badge."""
        return {
            ProjectStatus.ON_TRACK: "#dcfce7",  # Light green
            ProjectStatus.AHEAD: "#dbeafe",  # Light blue
            ProjectStatus.SLIGHT_DELAY: "#fef3c7",  # Light amber
            ProjectStatus.AT_RISK: "#fee2e2",  # Light red
        }[status]

    def _render_progress_chart(self, on_track: int, total: int) -> str:
        """Render a simple horizontal bar chart showing project health."""
        if total == 0:
            return ""

        percentage = int((on_track / total) * 100)

        # Use table-based bar for better email client compatibility
        green_width = percentage
        gray_width = 100 - percentage

        return f"""
        <div style="margin: 24px 0 0 0; padding: 16px 0;">
            <div style="font-size: 14px; font-weight: 600; color: #5f6368; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                📊 Project Health
            </div>
            <table cellpadding="0" cellspacing="0" border="0" style="width: 100%; margin: 0 0 8px 0;">
                <tr>
                    <td width="{green_width}%" style="background-color: #34a853; height: 24px; border-radius: 4px 0 0 4px; font-size: 1px; line-height: 1px;">&nbsp;</td>
                    <td width="{gray_width}%" style="background-color: #e8eaed; height: 24px; border-radius: 0 4px 4px 0; font-size: 1px; line-height: 1px;">&nbsp;</td>
                </tr>
            </table>
            <div style="font-size: 13px; color: #5f6368;">
                {on_track} of {total} projects on track or ahead ({percentage}%)
            </div>
        </div>
        """

    def _render_plain_text_fallback(
        self, report: WeeklyReport, ai_intro: Optional[str], github_stats: Optional[str]
    ) -> str:
        """Generate plain text fallback."""
        parts = []

        parts.append(f"WEEKLY ENGINEERING UPDATE")
        parts.append(
            f"{report.week_start.strftime('%B %d')} – {report.week_end.strftime('%B %d, %Y')}"
        )
        parts.append("=" * 60)
        parts.append("")

        if ai_intro:
            parts.append(ai_intro)
            parts.append("")

        parts.append("Greetings Everyone,")
        parts.append("")
        parts.append("Here's this week's progress across active projects:")
        parts.append("")

        for idx, project in enumerate(report.projects, start=1):
            status_display = project.status_text or project.status.display_name()
            parts.append(f"{idx}. {project.name}")
            parts.append(f"   Status: {status_display}")
            parts.append(f"   Completed: {project.completed}")
            parts.append(f"   In Progress: {project.in_progress}")
            parts.append(f"   Blockers: {project.blockers}")
            parts.append(f"   Next Week: {project.next_week}")
            parts.append("")

        # Bugs/tickets
        if (
            hasattr(report, "bugs_fixed")
            or hasattr(report, "tickets_resolved")
            or hasattr(report, "features_shipped")
        ):
            bugs_fixed = getattr(report, "bugs_fixed", 0)
            tickets_resolved = getattr(report, "tickets_resolved", 0)
            features_shipped = getattr(report, "features_shipped", 0)

            if bugs_fixed > 0 or tickets_resolved > 0 or features_shipped > 0:
                parts.append("BUGS FIXED & ISSUES RESOLVED")
                parts.append("-" * 60)
                items = []
                if tickets_resolved > 0:
                    items.append(f"{tickets_resolved} tickets")
                if bugs_fixed > 0:
                    items.append(f"{bugs_fixed} bugs")
                if features_shipped > 0:
                    items.append(f"{features_shipped} features")
                parts.append(", ".join(items))
                parts.append("")

        parts.append("OVERALL SUMMARY")
        parts.append("-" * 60)
        for bullet in report.summary_bullets:
            parts.append(f"• {bullet}")
        if github_stats:
            parts.append(f"• {github_stats}")
        parts.append("")

        on_track = report.get_on_track_count()
        total = report.get_total_count()
        percentage = int((on_track / total) * 100) if total > 0 else 0
        parts.append(f"PROJECT HEALTH: {on_track}/{total} on track ({percentage}%)")
        parts.append("")

        milestone_date = (
            report.next_milestone_date.strftime("%b %d, %Y")
            if report.next_milestone_date
            else "TBD"
        )
        parts.append(f"NEXT MILESTONE: {report.next_milestone} — {milestone_date}")
        parts.append("")

        parts.append("Best,")
        parts.append(report.lead_name)
        parts.append("Software Engineer")
        parts.append(f"({report.team_name})")

        return "\n".join(parts)


if __name__ == "__main__":
    # Test with sample data
    from datetime import date
    from data.models import ProjectStatus
    from pathlib import Path

    report = WeeklyReport(
        week_start=date(2025, 10, 6),
        week_end=date(2025, 10, 11),
        lead_name="Sebastian Lee",
        team_name="Product Engineering",
        projects=[
            ProjectUpdate(
                name="API Platform",
                status=ProjectStatus.ON_TRACK,
                completed="Authentication refactor, rate limiter implementation",
                in_progress="Endpoint pagination, caching optimization",
                blockers="None",
                next_week="Deploy v2.3 to staging, begin load testing",
            ),
            ProjectUpdate(
                name="Web Application",
                status=ProjectStatus.SLIGHT_DELAY,
                status_text="Minor delay",
                completed="Dashboard backend, notification system",
                in_progress="Frontend integration",
                blockers="Waiting on design assets",
                next_week="Complete analytics integration",
            ),
        ],
        summary_bullets=[
            "2/2 projects progressing well",
            "Minor delay on Web App due to design dependency",
        ],
        next_milestone="Sprint 15 completion",
        next_milestone_date=date(2025, 10, 18),
    )

    # Add bugs/tickets data dynamically
    report.bugs_fixed = 5
    report.tickets_resolved = 20
    report.features_shipped = 2

    renderer = HTMLEmailRenderer()
    ai_intro = "Hello! I'm Sebastian's AI assistant. This week showed solid progress—our API Platform is humming along nicely and the Web App just needs those design assets to wrap up."
    github_stats = "23 commits across 3 repos, 4 PRs merged"

    subject, html, plain = renderer.render(
        report, ai_intro=ai_intro, github_stats=github_stats
    )

    output = Path("test_email.html")
    output.write_text(html)
    print(f"✓ HTML saved to {output}")
    print(f"✓ Subject: {subject}")
