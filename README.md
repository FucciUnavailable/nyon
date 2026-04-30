# Weekly Report System - Complete Guide

## Overview

This system generates and sends weekly engineering progress reports via email. It combines project updates, AI-generated summaries, GitHub activity stats, and automated email delivery through SendGrid.

---

## Quick Start

```bash
uv sync
uv pip install -r requirements.txt
uv run python tui.py
```

That's it. The TUI handles everything — creating reports, editing projects, previewing, and sending.

---

## TUI Workflow

```bash
uv run python tui.py
```

### Home screen

Shows the status of `projects.json` (lead, team, week, project count) and three buttons:

- **New Report** — start a fresh report from scratch
- **Edit Report** — edit the current `projects.json`
- **Preview & Send** — render and send the email

Keyboard shortcuts: `Q` to quit, `Escape` to go back from any screen.

---

### Editing a report

Two tabs:

**Report Details** — lead name, team, week dates, summary bullets, bugs/tickets metrics, next milestone.

**Projects** — a table of all projects with Add / Edit / Remove buttons. Each project has: name, status (🟢🟡🔵🔴), status description, completed work, in-progress work, blockers, next-week plans, optional progress % and ETA.

`Ctrl+S` saves and writes `projects.json`.

---

### Preview & Send

Left panel: toggles for AI summary and GitHub stats, AI style selector (executive / casual / detailed), optional schedule field (YYYY-MM-DD HH:MM UTC).

Right panel: rendered email preview.

- **Generate Preview** — renders the email without sending
- **Send Now** — sends immediately (or at the scheduled time if a schedule is set)

---

## What Each Component Does

### 1. **`weekly_report.py`** (Main Entry Point)

**Location:** Root directory
**Purpose:** Simple interactive wrapper that guides you through the entire process
**Why it exists:** Bypasses complex CLI flags and provides an intuitive interface

**Flow:**
```
Check projects.json exists
  ↓
Ask: Preview or Send?
  ↓
Ask: Include AI? Include GitHub?
  ↓
(If sending) Offer to archive to weekly_logs/
  ↓
Call generate_weekly_report.generate()
  ↓
Show success message
```

---

### 2. **`scripts/create_projects_json.py`** (Data Collection)

**Purpose:** Interactive wizard to build your `projects.json` file

**Collects:**
- Week start/end dates (auto-detected or manual)
- Your name and team name
- For each project:
  - Project name
  - Status (🟢 On Track, 🟡 Slight Delay, 🔵 Ahead, 🔴 At Risk)
  - What was completed this week
  - What's in progress
  - Any blockers
  - Plans for next week
- Overall summary bullets
- Next milestone name and date

**Output:** Valid JSON file that passes all Pydantic validations

---

### 3. **`scripts/generate_weekly_report.py`** (Core Generator)

**Purpose:** Master orchestrator that combines everything

**Steps:**

1. **Load project data** (`load_report()`)
   - Reads `projects.json`
   - Validates with Pydantic models
   - Raises errors if invalid

2. **Generate AI summary** (optional)
   - Uses OpenAI GPT-4o-mini
   - Reads project data and creates 2-3 line friendly intro
   - Styles: executive / casual / detailed
   - Falls back gracefully if API fails

3. **Collect GitHub stats** (optional)
   - Queries GitHub API for last 7 days
   - Counts commits, PRs opened/merged, issues closed
   - Formats as one-line summary
   - Falls back gracefully if API fails

4. **Render email**
   - Uses `PlainTextEmailRenderer`
   - Combines all sections into plain text email
   - Generates subject line with dates and project names

5. **Preview**
   - Shows rich console preview of final email

6. **Send** (if not dry-run)
   - Gets recipients from `.env` config
   - Sends via SendGrid API
   - Confirms delivery

**CLI Flags (if calling directly):**
```bash
python -m scripts.generate_weekly_report \
  --input projects.json \
  --dry-run \
  --skip-ai \
  --skip-github \
  --style executive \
  --github-days 7 \
  --to "email1@example.com,email2@example.com"
```

---

### 4. **`core/email_renderer.py`** (Email Formatting)

**Purpose:** Converts structured report data into formatted email text

**Class:** `PlainTextEmailRenderer`

**Template Structure:**

```
[🤖 AI Intro if enabled]
---

Hi team,

Here's a summary of this week's progress across active projects:

### 1. Project Name
Status: 🟢 On Track
Progress:
- Completed: [what was done]
- In Progress: [what's being worked on]
- Blockers: [any issues]
Next Week:
- [plans]

### 2. [More projects...]

Overall Summary:
- [auto-generated bullet: X/Y projects on track]
- [custom bullets]
- 💻 [GitHub stats if enabled]

Next Milestone:
- [milestone name] — [date]

Best,
[Your Name]
Software Engineer
([Team Name])
```

**Note:** Currently generates plain text with markdown-style formatting (`###`, `-`, etc.). This doesn't render well in most email clients.

---

### 5. **`ai/summarizer.py`** (AI Summary Generation)

**Purpose:** Generates friendly 2-3 line AI intros using OpenAI

**How it works:**
1. Builds context from project data (status, completed work, blockers)
2. Sends to OpenAI with style-specific instructions
3. Returns summary like:
   - *"Hi there! This is Claude, Sebastian's AI assistant. This week showed solid progress with 3/4 projects on track. The API Platform hit all milestones while the Web App has a minor delay waiting on design assets."*

**API:** Uses OpenAI GPT-4o-mini (cheapest model)
**Token limit:** 150 tokens max
**Temperature:** 0.7 (balanced creativity)

**Configured in `.env`:**
- `OPENAI_API_KEY`
- `AI_SYSTEM_PROMPT` (optional override)
- `AI_MAX_TOKENS` (optional)
- `AI_TEMPERATURE` (optional)

---

### 6. **`core/github_collector.py`** (GitHub Stats)

**Purpose:** Collects GitHub activity stats for the past 7 days

**What it tracks:**
- Commits pushed
- Pull requests opened
- Pull requests merged
- Issues closed
- Across all configured repositories

**Output:** One-line summary like:
```
"This week: 23 commits, 5 PRs opened (4 merged), 3 issues closed"
```

**Configured in `.env`:**
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_REPOS=owner/repo1,owner/repo2,owner/repo3
```

---

### 7. **`core/email_sender.py`** (SendGrid Integration)

**Purpose:** Sends emails via SendGrid API

**Flow:**
1. Formats plain text email
2. Calls SendGrid API with:
   - From address (configured in `.env`)
   - To addresses (from config or CLI override)
   - Subject line
   - Body text
3. Handles errors and retries

**Configured in `.env`:**
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=reports@yourcompany.com
REPORT_RECIPIENT_EMAILS=manager@company.com,team@company.com
```

---

### 8. **`data/models.py`** (Data Validation)

**Purpose:** Pydantic models for type safety and validation

**Models:**

#### `ProjectStatus` (Enum)
- `ON_TRACK` → 🟢 On Track
- `SLIGHT_DELAY` → 🟡 Slight Delay
- `AHEAD` → 🔵 Ahead of Schedule
- `AT_RISK` → 🔴 At Risk

#### `ProjectUpdate`
- `name`: Project name (required)
- `status`: ProjectStatus (default: ON_TRACK)
- `status_text`: Custom status description
- `completed`: What was done this week
- `in_progress`: Current work
- `blockers`: Issues blocking progress
- `next_week`: Plans for next week

#### `WeeklyReport`
- `week_start`: Start date
- `week_end`: End date (validated to be after start)
- `lead_name`: Your name (required)
- `team_name`: Team name (default: "Product Engineering")
- `projects`: List of ProjectUpdate (min 1 required)
- `summary_bullets`: Overall summary points
- `next_milestone`: Next major milestone
- `next_milestone_date`: Target date (optional)

**Validation:**
- Ensures dates are valid
- Ensures at least one project exists
- Trims whitespace from names
- Validates project names aren't empty

---

## Configuration (`.env` File)

Create a `.env` file in the root directory with:

```env
# GitHub Integration
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_REPOS=username/repo1,username/repo2

# SendGrid Email
SENDGRID_API_KEY=SG.your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your-email@company.com
REPORT_RECIPIENT_EMAILS=recipient1@company.com,recipient2@company.com

# OpenAI for AI Summaries
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Optional AI Settings
AI_SYSTEM_PROMPT="You are a helpful engineering assistant..."
AI_MAX_TOKENS=150
AI_TEMPERATURE=0.7

# Report Settings
REPORT_OUTPUT_DIR=./reports
LOG_LEVEL=INFO
```

---

## Directory Structure

```
nyon/
├── tui.py                        # TUI entry point (start here)
├── weekly_report.py              # Legacy CLI entry point
├── projects.json                 # Current week's report data (generated)
├── weekly_logs/                  # Archived reports (auto-created)
│   ├── report_2025-10-07.json
│   └── report_2025-10-14.json
├── scripts/
│   ├── create_projects_json.py   # Interactive data collection
│   └── generate_weekly_report.py # Core report generator
├── core/
│   ├── email_renderer.py         # Email template rendering
│   ├── email_sender.py           # SendGrid integration
│   └── github_collector.py       # GitHub API client
├── ai/
│   └── summarizer.py             # OpenAI integration
├── data/
│   ├── models.py                 # Pydantic data models
│   └── github_models.py          # GitHub-specific models
├── config/
│   └── settings.py               # Configuration management
├── utils/
│   ├── json_exporter.py          # JSON file writer
│   ├── github_stats_formatter.py # Format GitHub stats
│   └── logger.py                 # Logging setup
└── .env                          # Configuration (not in git)
```

---

## Logging and History

### Where Reports Are Saved

1. **Current report:** `projects.json` (root directory)
   - Overwrites each time you create a new one

2. **Archived reports:** `weekly_logs/report_YYYY-MM-DD.json`
   - Only saved when you choose "send" mode
   - Only saved if you confirm the archive prompt
   - Named by week start date
   - Permanent historical record

### Why This Matters

- If you only use "preview" mode, **nothing gets archived**
- The `weekly_logs/` directory will remain empty
- Only reports that are actually sent get logged
- This is intentional to avoid cluttering logs with drafts

---

## Common Use Cases

### 1. First Time Setup
```bash
# Clone and install
uv sync
uv pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Fill in GITHUB_TOKEN, SENDGRID_API_KEY, OPENAI_API_KEY, etc.

# Launch the TUI
uv run python tui.py
# Hit "New Report" to create your first report, then "Preview & Send" to test
```

### 2. Weekly Report Routine
```bash
uv run python tui.py
# → New Report (or Edit Report if updating last week's)
# → Fill in project details, save
# → Preview & Send → Generate Preview
# → Send Now when ready
```

### 3. Send Without AI/GitHub
```bash
uv run python tui.py
# → Preview & Send
# → Toggle off AI Summary and GitHub Stats
# → Generate Preview, then Send Now
```

### 4. Manual CLI (Advanced)
```bash
# Full control over all options
uv run python -m scripts.generate_weekly_report \
  --input projects.json \
  --style casual \
  --github-days 14 \
  --to "override@example.com"
```

---

## Troubleshooting

### Error: `'NoneType' object has no attribute 'read_text'`
**Cause:** No `--input` flag provided when calling `generate_weekly_report.py` directly
**Fix:** Use `python weekly_report.py` instead, or add `--input projects.json`

### Error: `No module named 'typer'`
**Cause:** Dependencies not installed
**Fix:** `source venv/bin/activate && pip install -r requirements.txt`

### Error: `Failed to load report: validation error`
**Cause:** Invalid data in `projects.json`
**Fix:** Delete `projects.json` and recreate with `python scripts/create_projects_json.py`

### Error: `SendGrid API error`
**Cause:** Invalid SendGrid API key or rate limit
**Fix:** Check `.env` file, verify key is valid in SendGrid dashboard

### Error: `OpenAI API error`
**Cause:** Invalid OpenAI key or quota exceeded
**Fix:** Use `--skip-ai` flag or check OpenAI account

### Empty `weekly_logs/` directory
**Cause:** Only previewing reports, never sending them
**Fix:** Choose "send" mode and confirm archiving to save logs

---

## Email Output Format (Current)

**Subject:**
```
Weekly Engineering Progress – 2025-10-07–2025-10-11 (API Platform, Web App)
```

**Body:** Plain text with markdown-style formatting
- Uses `###` for headers
- Uses `-` for bullets
- Uses emojis (🟢, 🟡, 🔴, 🔵, 🤖, 💻)
- No HTML styling

**Issue:** Markdown doesn't render in most email clients (Gmail, Outlook, etc.)
**Result:** Recipients see raw markdown syntax like `###` and `-`
**Needed:** HTML email renderer with proper styling

---

## Next Improvements Needed

1. **HTML Email Renderer**
   - Replace plain text with HTML email template
   - Add proper styling (headers, colors, spacing)
   - Make it look professional in Gmail/Outlook
   - Keep plain text as fallback

2. **Automatic Archiving**
   - Save to `weekly_logs/` even in preview mode
   - Add timestamped backups before overwriting `projects.json`

3. **Email Template Improvements**
   - Better visual hierarchy
   - Status badges with colors
   - Responsive design for mobile
   - Company branding

---

## API Costs

**OpenAI (AI Summaries):**
- Model: GPT-4o-mini
- Cost: ~$0.0001 per report
- Max tokens: 150

**GitHub API:**
- Free (5,000 requests/hour with token)

**SendGrid:**
- Free tier: 100 emails/day
- Each report = 1 email per recipient

**Estimated cost for weekly reports:** < $0.01/week

---

## Security Notes

- **Never commit `.env` file** - Contains API keys
- `.gitignore` includes `.env`, `projects.json`, `weekly_logs/`
- GitHub token needs: `repo` scope (read access)
- SendGrid key needs: `Mail Send` permission only
- OpenAI key: Standard API access

---

## Summary

The system provides a **complete end-to-end workflow** for weekly engineering reports:

1. **Data Collection** → Interactive wizard (`create_projects_json.py`)
2. **AI Enhancement** → OpenAI summary (`ai/summarizer.py`)
3. **GitHub Stats** → Activity tracking (`core/github_collector.py`)
4. **Email Rendering** → Text formatting (`core/email_renderer.py`)
5. **Delivery** → SendGrid sending (`core/email_sender.py`)
6. **Archiving** → Historical logs (`weekly_logs/`)

**Main Entry Point:** `python weekly_report.py`

**Just run it and follow the prompts!**
