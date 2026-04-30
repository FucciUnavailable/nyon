#!/usr/bin/env python3
"""Textual TUI for Nyon weekly report generator. Run: python tui.py"""

import json
import sys
import asyncio
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

try:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical, ScrollableContainer, Container
    from textual.screen import Screen, ModalScreen
    from textual.widgets import (
        Button, DataTable, Footer, Header, Input, Label,
        Select, Static, Switch, TabbedContent, TabPane, TextArea,
    )
except ImportError:
    print("Textual not installed. Run: pip install 'textual>=0.60'")
    sys.exit(1)

PROJECTS_FILE = Path("projects.json")

STATUS_OPTIONS: List[tuple] = [
    ("🟢 On Track", "on_track"),
    ("🟡 Slight Delay", "slight_delay"),
    ("🔵 Ahead", "ahead"),
    ("🔴 At Risk", "at_risk"),
]
STATUS_EMOJI = {"on_track": "🟢", "slight_delay": "🟡", "ahead": "🔵", "at_risk": "🔴"}
STYLE_OPTIONS: List[tuple] = [
    ("Executive", "executive"),
    ("Casual", "casual"),
    ("Detailed", "detailed"),
]


# ── Project Modal ─────────────────────────────────────────────────────────────

class ProjectModal(ModalScreen):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, project: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self._project: Dict[str, Any] = project or {}

    def compose(self) -> ComposeResult:
        p = self._project
        # Blank out sentinel "None" values so the form is clean
        def val(key: str, default: str = "") -> str:
            v = p.get(key, default)
            return "" if v in ("None", "TBD", None) else str(v)

        with ScrollableContainer(classes="modal-dialog"):
            yield Label("Project Details", classes="section-title")
            yield Label("Name *")
            yield Input(val("name"), id="proj-name", placeholder="Project name")
            yield Label("Status")
            yield Select(STATUS_OPTIONS, value=p.get("status", "on_track"), id="proj-status")
            yield Label("Status description")
            yield Input(val("status_text"), id="proj-status-text", placeholder="e.g. On track for Q2")
            yield Label("Completed this week")
            yield TextArea(val("completed"), id="proj-completed")
            yield Label("In progress")
            yield TextArea(val("in_progress"), id="proj-in-progress")
            yield Label("Blockers")
            yield TextArea(val("blockers"), id="proj-blockers")
            yield Label("Plans for next week")
            yield TextArea(val("next_week"), id="proj-next-week")
            yield Label("Progress % (optional, 0–100)")
            yield Input(val("progress_percent"), id="proj-progress", placeholder="75")
            yield Label("ETA (optional, YYYY-MM-DD)")
            yield Input(val("eta"), id="proj-eta", placeholder="2026-06-01")
            with Horizontal(classes="modal-actions"):
                yield Button("Save", variant="success", id="proj-save")
                yield Button("Cancel", id="proj-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "proj-cancel":
            self.dismiss(None)
        elif event.button.id == "proj-save":
            self._save()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _save(self) -> None:
        name = self.query_one("#proj-name", Input).value.strip()
        if not name:
            self.notify("Project name is required", severity="error")
            return

        prog_str = self.query_one("#proj-progress", Input).value.strip()
        progress = int(prog_str) if prog_str.isdigit() else None
        eta_str = self.query_one("#proj-eta", Input).value.strip()
        status_val = self.query_one("#proj-status", Select).value
        if status_val is Select.BLANK:
            status_val = "on_track"

        self.dismiss({
            "name": name,
            "status": status_val,
            "status_text": self.query_one("#proj-status-text", Input).value.strip(),
            "completed": self.query_one("#proj-completed", TextArea).text.strip() or "None",
            "in_progress": self.query_one("#proj-in-progress", TextArea).text.strip() or "None",
            "blockers": self.query_one("#proj-blockers", TextArea).text.strip() or "None",
            "next_week": self.query_one("#proj-next-week", TextArea).text.strip() or "TBD",
            "progress_percent": progress,
            "eta": eta_str or None,
        })


# ── Report Form Screen ────────────────────────────────────────────────────────

class ReportFormScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "save", "Save"),
    ]
    SUB_TITLE = "Edit Report"

    def __init__(self, report_data: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self._data = report_data or {}
        self._projects: List[Dict[str, Any]] = list(self._data.get("projects", []))
        self._edit_idx: Optional[int] = None

    def compose(self) -> ComposeResult:
        d = self._data
        today = date.today()
        ws = today - timedelta(days=today.weekday())
        we = ws + timedelta(days=4)

        yield Header()
        with TabbedContent(id="form-tabs"):
            with TabPane("Report Details", id="tab-details"):
                with ScrollableContainer():
                    yield Label("Lead name")
                    yield Input(d.get("lead_name", "Amine"), id="lead-name")
                    yield Label("Team name")
                    yield Input(d.get("team_name", "PTR"), id="team-name")
                    yield Label("Week start (YYYY-MM-DD)")
                    yield Input(d.get("week_start", str(ws)), id="week-start")
                    yield Label("Week end (YYYY-MM-DD)")
                    yield Input(d.get("week_end", str(we)), id="week-end")
                    yield Label("Summary bullets (one per line)")
                    yield TextArea("\n".join(d.get("summary_bullets", [])), id="summary-bullets")
                    yield Label("Bugs fixed")
                    yield Input(str(d.get("bugs_fixed", 0)), id="bugs-fixed")
                    yield Label("Tickets resolved")
                    yield Input(str(d.get("tickets_resolved", 0)), id="tickets-resolved")
                    yield Label("Tickets open")
                    yield Input(str(d.get("tickets_open", 0)), id="tickets-open")
                    yield Label("Features shipped")
                    yield Input(str(d.get("features_shipped", 0)), id="features-shipped")
                    yield Label("Next milestone")
                    yield Input(d.get("next_milestone", "TBD"), id="next-milestone")
                    yield Label("Milestone date (optional, YYYY-MM-DD)")
                    yield Input(d.get("next_milestone_date", "") or "", id="milestone-date")

            with TabPane("Projects", id="tab-projects"):
                with Vertical(id="projects-tab-content"):
                    with Horizontal(classes="project-actions"):
                        yield Button("＋ Add", variant="primary", id="proj-add")
                        yield Button("✎ Edit", id="proj-edit")
                        yield Button("✕ Remove", variant="error", id="proj-remove")
                    yield DataTable(id="projects-table", cursor_type="row")

        with Horizontal(classes="form-actions"):
            yield Button("Save", variant="success", id="form-save")
            yield Button("Cancel", id="form-cancel")
        yield Footer()

    def on_mount(self) -> None:
        self.call_after_refresh(self._refresh_table)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if str(event.tab.id).endswith("tab-projects"):
            self._refresh_table()

    def _refresh_table(self) -> None:
        table = self.query_one("#projects-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Name", "Status", "Progress", "ETA")
        for p in self._projects:
            status = p.get("status", "on_track")
            emoji = STATUS_EMOJI.get(status, "⚪")
            prog = f"{p['progress_percent']}%" if p.get("progress_percent") is not None else "—"
            table.add_row(p.get("name", ""), f"{emoji} {status}", prog, p.get("eta") or "—")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "proj-add":
            self.app.push_screen(ProjectModal(), self._on_project_added)
        elif btn == "proj-edit":
            row = self.query_one("#projects-table", DataTable).cursor_row
            if 0 <= row < len(self._projects):
                self._edit_idx = row
                self.app.push_screen(ProjectModal(self._projects[row]), self._on_project_edited)
        elif btn == "proj-remove":
            row = self.query_one("#projects-table", DataTable).cursor_row
            if 0 <= row < len(self._projects):
                self._projects.pop(row)
                self._refresh_table()
        elif btn == "form-save":
            self.action_save()
        elif btn == "form-cancel":
            self.action_go_back()

    def _on_project_added(self, result: Optional[Dict]) -> None:
        if result:
            self._projects.append(result)
            self._refresh_table()

    def _on_project_edited(self, result: Optional[Dict]) -> None:
        if result is not None and self._edit_idx is not None:
            self._projects[self._edit_idx] = result
            self._edit_idx = None
            self._refresh_table()

    def action_save(self) -> None:
        if not self._projects:
            self.notify("Add at least one project before saving", severity="error")
            return
        try:
            bullets_text = self.query_one("#summary-bullets", TextArea).text.strip()
            bullets = [b.strip() for b in bullets_text.splitlines() if b.strip()]
            if not bullets:
                on_track = sum(1 for p in self._projects if p.get("status") in ("on_track", "ahead"))
                bullets = [f"{on_track}/{len(self._projects)} projects on or ahead of schedule"]

            data: Dict[str, Any] = {
                "lead_name": self.query_one("#lead-name", Input).value.strip(),
                "team_name": self.query_one("#team-name", Input).value.strip(),
                "week_start": self.query_one("#week-start", Input).value.strip(),
                "week_end": self.query_one("#week-end", Input).value.strip(),
                "projects": self._projects,
                "summary_bullets": bullets,
                "bugs_fixed": int(self.query_one("#bugs-fixed", Input).value or 0),
                "tickets_resolved": int(self.query_one("#tickets-resolved", Input).value or 0),
                "tickets_open": int(self.query_one("#tickets-open", Input).value or 0),
                "features_shipped": int(self.query_one("#features-shipped", Input).value or 0),
                "next_milestone": self.query_one("#next-milestone", Input).value.strip(),
                "next_milestone_date": self.query_one("#milestone-date", Input).value.strip() or None,
            }

            from data.models import WeeklyReport
            from utils.json_exporter import JSONExporter
            JSONExporter().export(WeeklyReport(**data), PROJECTS_FILE)
            self.notify("Saved to projects.json", severity="information")
            self.app.pop_screen()
        except Exception as exc:
            self.notify(f"Save failed: {exc}", severity="error", timeout=8)

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ── Preview & Send Screen ─────────────────────────────────────────────────────

class PreviewSendScreen(Screen):
    BINDINGS = [Binding("escape", "go_back", "Back")]
    SUB_TITLE = "Preview & Send"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="preview-layout"):
            with Vertical(classes="options-panel"):
                yield Label("Options", classes="section-title")
                yield Label("AI Summary")
                yield Switch(value=True, id="use-ai")
                yield Label("GitHub Stats")
                yield Switch(value=False, id="use-github")
                yield Label("AI Style")
                yield Select(STYLE_OPTIONS, value="executive", id="ai-style")
                yield Label("Schedule send (optional)\nYYYY-MM-DD HH:MM UTC")
                yield Input("", id="schedule", placeholder="blank = send now")
                yield Button("Generate Preview", variant="primary", id="btn-preview")
                yield Button("Send Now", variant="success", id="btn-send")
                yield Button("Back", id="btn-back")
            with Vertical(classes="preview-panel"):
                yield Label("Email Preview", classes="section-title")
                yield TextArea(
                    "Press Generate Preview to render the email.",
                    id="preview-area",
                    read_only=True,
                )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "btn-back":
            self.action_go_back()
        elif btn == "btn-preview":
            self.run_worker(self._do_preview(), exclusive=True)
        elif btn == "btn-send":
            self.run_worker(self._do_send(), exclusive=True)

    async def _do_preview(self) -> None:
        self._set_preview("Generating preview…")
        try:
            subject, plain = await self._render_report()
            self._set_preview(f"Subject: {subject}\n{'─' * 60}\n\n{plain}")
        except Exception as exc:
            self._set_preview(f"Error: {exc}")

    async def _do_send(self) -> None:
        if not PROJECTS_FILE.exists():
            self.notify("No projects.json found — create one first", severity="error")
            return
        self._set_preview("Sending…")
        try:
            subject, _plain = await self._render_report()
            await self._send_email(subject)
        except Exception as exc:
            self._set_preview(f"Error: {exc}")

    async def _render_report(self):
        from scripts.generate_weekly_report import generate_ai_summary, collect_github_stats, load_report
        from core.html_email_renderer import HTMLEmailRenderer

        skip_ai = not self.query_one("#use-ai", Switch).value
        skip_github = not self.query_one("#use-github", Switch).value
        style_val = self.query_one("#ai-style", Select).value
        style = str(style_val) if style_val is not Select.BLANK else "executive"

        report = load_report(PROJECTS_FILE)

        ai_intro = None
        if not skip_ai:
            ai_intro = await generate_ai_summary(report, style)

        github_stats = None
        if not skip_github:
            github_stats = await asyncio.to_thread(collect_github_stats, 7)

        subject, html_body, plain_body = HTMLEmailRenderer().render(
            report, ai_intro=ai_intro, github_stats=github_stats
        )
        self._last_render = (subject, html_body, plain_body)
        return subject, plain_body

    async def _send_email(self, subject: str) -> None:
        from scripts.generate_weekly_report import send_email_async, parse_schedule
        from config.settings import settings

        schedule_str = self.query_one("#schedule", Input).value.strip()
        send_at = parse_schedule(schedule_str) if schedule_str else None

        _, html_body, plain_body = self._last_render
        to_emails = settings.get_recipients_list()
        await send_email_async(to_emails, subject, html_body, plain_body, send_at)

        action = f"Scheduled for {schedule_str}" if send_at else "Sent"
        self._set_preview(
            f"✓ {action} successfully!\n\n"
            f"Subject: {subject}\nTo: {', '.join(to_emails)}"
        )
        self.notify("Report sent!", severity="information")

    def _set_preview(self, text: str) -> None:
        self.query_one("#preview-area", TextArea).load_text(text)

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ── Home Screen ───────────────────────────────────────────────────────────────

class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="home-wrap"):
            yield Static("Nyon — Weekly Report", classes="home-title")
            yield Static("", id="home-status", classes="home-status")
            yield Button("New Report", id="home-new", variant="primary")
            yield Button("Edit Report", id="home-edit")
            yield Button("Preview & Send", id="home-preview", variant="success")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def on_screen_resume(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        status_w = self.query_one("#home-status", Static)
        edit_btn = self.query_one("#home-edit", Button)
        preview_btn = self.query_one("#home-preview", Button)

        if PROJECTS_FILE.exists():
            try:
                d = json.loads(PROJECTS_FILE.read_text())
                projects = d.get("projects", [])
                on_track = sum(1 for p in projects if p.get("status") in ("on_track", "ahead"))
                status_w.update(
                    f"[green]● Report loaded[/green]\n"
                    f"  {d.get('lead_name', '?')} · {d.get('team_name', '?')} · "
                    f"Week of {d.get('week_start', '?')}\n"
                    f"  {len(projects)} project(s)  ·  {on_track} on track"
                )
                edit_btn.disabled = False
                preview_btn.disabled = False
            except Exception:
                status_w.update("[red]● projects.json is invalid — try editing it[/red]")
                edit_btn.disabled = False
                preview_btn.disabled = True
        else:
            status_w.update("[yellow]● No report found — start with New Report[/yellow]")
            edit_btn.disabled = True
            preview_btn.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "home-new":
            self.app.push_screen(ReportFormScreen())
        elif btn == "home-edit" and PROJECTS_FILE.exists():
            self.app.push_screen(ReportFormScreen(json.loads(PROJECTS_FILE.read_text())))
        elif btn == "home-preview":
            self.app.push_screen(PreviewSendScreen())


# ── App ───────────────────────────────────────────────────────────────────────

class NyonApp(App):
    TITLE = "Nyon"
    SUB_TITLE = "Weekly Report"
    BINDINGS = [Binding("q", "quit", "Quit")]

    CSS = """
    /* ── Home ──────────────────────────────────────────────────────── */
    HomeScreen .home-wrap {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    HomeScreen .home-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 1;
    }
    HomeScreen .home-status {
        border: round $primary-darken-1;
        padding: 1 2;
        width: 54;
        height: auto;
        margin-bottom: 2;
    }
    HomeScreen Button {
        width: 54;
        margin-bottom: 1;
    }

    /* ── Project Modal ──────────────────────────────────────────────── */
    ProjectModal {
        align: center middle;
    }
    .modal-dialog {
        width: 72;
        height: 85%;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    .modal-dialog Label {
        color: $text-muted;
        margin-top: 1;
    }
    .modal-dialog TextArea {
        height: 5;
    }
    .modal-actions {
        margin-top: 1;
        height: 3;
        align: left middle;
    }
    .modal-actions Button {
        margin-right: 1;
    }

    /* ── Report Form ────────────────────────────────────────────────── */
    ReportFormScreen #form-tabs {
        height: 1fr;
    }
    ReportFormScreen ScrollableContainer {
        padding: 0 2;
    }
    ReportFormScreen Label {
        color: $text-muted;
        margin-top: 1;
    }
    ReportFormScreen TextArea {
        height: 5;
    }
    ReportFormScreen TabPane {
        height: 1fr;
    }
    #projects-tab-content {
        height: 1fr;
    }
    #projects-table {
        height: 1fr;
    }
    .project-actions {
        padding: 1 0;
        height: 4;
        align: left middle;
    }
    .project-actions Button {
        margin-right: 1;
    }
    .form-actions {
        height: 5;
        border-top: solid $primary-darken-2;
        align: left middle;
        padding: 1 2;
    }
    .form-actions Button {
        margin-right: 1;
    }

    /* ── Preview / Send ─────────────────────────────────────────────── */
    #preview-layout {
        height: 1fr;
    }
    .options-panel {
        width: 34;
        border-right: solid $primary-darken-2;
        padding: 1 2;
        overflow-y: auto;
    }
    .options-panel Label {
        color: $text-muted;
        margin-top: 1;
    }
    .options-panel Button {
        width: 100%;
        margin-top: 1;
    }
    .preview-panel {
        width: 1fr;
        padding: 1 2;
    }
    .preview-panel TextArea {
        height: 1fr;
    }

    /* ── Shared ─────────────────────────────────────────────────────── */
    .section-title {
        text-style: bold;
        color: $accent;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


if __name__ == "__main__":
    NyonApp().run()
