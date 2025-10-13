# Quick Start Guide - Weekly Reports

## 🚀 Simple 3-Step Workflow

### Every Week (5 minutes):

#### **Step 1: Create Your Report**
```bash
python scripts/create_projects_json.py
```

This interactive wizard will ask you:
- Week dates (auto-filled for current week)
- Your name and team
- For each project:
  - Project name
  - Status (on_track, slight_delay, ahead, at_risk)
  - What you completed
  - What's in progress
  - Any blockers
  - Next week's plan
- Overall summary bullets
- Next milestone

**Output:** Creates `projects.json`

---

#### **Step 2: Generate & Send Report**
```bash
python weekly_report.py
```

This will:
1. Find your `projects.json`
2. Ask if you want to preview or send
3. Ask if you want AI summary and GitHub stats
4. Generate the report with AI
5. Send via SendGrid (or preview in terminal)
6. Optionally archive to `weekly_logs/`

**That's it!** Your report is sent.

---

## 📁 File Organization

Your weekly reports are automatically organized:

```
nyon/
├── projects.json              # Current week's report (working file)
└── weekly_logs/               # Archive of past reports
    ├── report_2025-10-06.json
    ├── report_2025-10-13.json
    └── report_2025-10-20.json
```

When you send a report, it's automatically archived to `weekly_logs/` with the date.

---

## 🎯 Common Workflows

### Quick Send (Default)
```bash
# 1. Create report
python scripts/create_projects_json.py

# 2. Send it
python weekly_report.py
# → Choose "send"
# → Enable AI summary
# → Skip GitHub stats (if not configured)
```

### Preview First
```bash
python weekly_report.py
# → Choose "preview"
# → Review the email in your terminal
# → Run again and choose "send" when ready
```

### Different AI Styles
```bash
python weekly_report.py
# → Choose AI summary: Yes
# → Pick style:
#    - executive: Professional, concise
#    - casual: Friendly, relaxed
#    - detailed: Comprehensive, technical
```

### Use Old Report
```bash
# Copy an old report from archive
cp weekly_logs/report_2025-10-06.json projects.json

# Edit it manually
nano projects.json

# Send it
python weekly_report.py
```

---

## 🔧 Advanced: Direct Commands

If you want more control, use the Python function directly:

### Preview with AI, skip GitHub
```bash
PYTHONPATH=. venv/bin/python -c "
from pathlib import Path
from scripts.generate_weekly_report import generate
generate(
    input_file=Path('projects.json'),
    dry_run=True,
    skip_ai=False,
    skip_github=True,
    github_days=7,
    style='executive',
    recipients=None
)
"
```

### Send to specific people
```bash
PYTHONPATH=. venv/bin/python -c "
from pathlib import Path
from scripts.generate_weekly_report import generate
generate(
    input_file=Path('projects.json'),
    dry_run=False,
    skip_ai=False,
    skip_github=True,
    github_days=7,
    style='executive',
    recipients='boss@company.com,team@company.com'
)
"
```

---

## 📝 Project Status Indicators

Use these in the wizard:

- `on_track` → 🟢 On Track (green)
- `slight_delay` → 🟡 Slight Delay (yellow)
- `ahead` → 🔵 Ahead of Schedule (blue)
- `at_risk` → 🔴 At Risk (red)

---

## 🎨 AI Summary Styles

**Executive** (default):
> "This week showed strong progress with 3/4 projects on track. The API Platform hit all milestones while the frontend team resolved design dependencies."

**Casual**:
> "Hey team! Great week overall - most projects cruising along nicely. API team crushed it, frontend had a tiny hiccup but back on track now."

**Detailed**:
> "This week's engineering efforts focused on three primary initiatives. The API Platform team successfully completed authentication refactoring and rate limiting implementation, achieving 100% test coverage. The frontend team encountered a dependency on design assets..."

---

## 🔍 Troubleshooting

### "No projects.json found"
Run: `python scripts/create_projects_json.py`

### "Module not found" errors
Make sure your venv is activated:
```bash
source venv/bin/activate
```

### GitHub stats failing
That's okay! GitHub integration is optional. Just skip it when prompted, or use `--skip-github`.

### Want to edit the JSON manually?
```bash
nano projects.json
```

Use this template:
```json
{
  "week_start": "2025-10-13",
  "week_end": "2025-10-20",
  "lead_name": "Your Name",
  "team_name": "Your Team",
  "projects": [
    {
      "name": "Project Name",
      "status": "on_track",
      "status_text": "On Track",
      "completed": "What you finished",
      "in_progress": "What you're working on",
      "blockers": "Any blockers or 'None'",
      "next_week": "Plans for next week"
    }
  ],
  "summary_bullets": [
    "Key point 1",
    "Key point 2"
  ],
  "next_milestone": "Milestone name",
  "next_milestone_date": "2025-10-27"
}
```

---

## ⏰ Automation Ideas

### Weekly Reminder
Add to your crontab (every Friday at 4pm):
```bash
crontab -e
# Add:
0 16 * * 5 cd /path/to/nyon && /path/to/venv/bin/python weekly_report.py
```

### Shell Alias
Add to your `.bashrc` or `.zshrc`:
```bash
alias weekly-report="cd ~/repos/nyon && python weekly_report.py"
alias new-report="cd ~/repos/nyon && python scripts/create_projects_json.py"
```

Then just type:
```bash
new-report    # Create
weekly-report # Send
```

---

## 📧 Email Configuration

Reports are sent to addresses in `.env`:
```bash
REPORT_RECIPIENT_EMAILS=manager@company.com,team@company.com,you@company.com
```

Edit this file to change recipients.

---

**Questions?** Check the main `README.md` or open an issue.
