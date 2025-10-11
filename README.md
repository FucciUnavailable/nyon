# 🚀 Engineering Intelligence System

An automated system for collecting GitHub activity, analyzing it with AI, and generating executive-ready reports.

## 📦 Installation

1. Clone the repository
2. Create a virtual environment:
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate


   ## 🎉 Final `README.md`

```markdown
# 🚀 Engineering Intelligence System

An automated weekly reporting system that combines project updates, AI-powered summaries, and GitHub activity tracking to generate professional engineering reports sent via email.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Weekly Workflow](#weekly-workflow)
- [CLI Reference](#cli-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## ✨ Features

- 📊 **Project Tracking**: Track multiple projects with status indicators (🟢 On Track, 🟡 Delayed, 🔵 Ahead, 🔴 At Risk)
- 🤖 **AI Summaries**: OpenAI-powered executive summaries introduce your reports in a friendly, professional tone
- 💻 **GitHub Integration**: Automatically collect PR and commit stats to validate project progress
- 📧 **Email Delivery**: Beautiful plain-text emails sent via SendGrid
- 🎨 **Rich CLI**: Interactive wizards and beautiful console output with `typer` and `rich`
- ⚙️ **Modular Design**: Clean architecture following best practices for maintainability

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Weekly Workflow                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Create projects.json           │
        │   (Manual or Interactive CLI)    │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   AI Summarizer (OpenAI)         │
        │   Generates 2-3 line intro       │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   GitHub Collector (Optional)    │
        │   Fetches PRs, commits, issues   │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Email Renderer                 │
        │   Combines all sections          │
        └──────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────┐
        │   Email Sender (SendGrid)        │
        │   Delivers to stakeholders       │
        └──────────────────────────────────┘
```

### Module Structure

```
project/
├── config/          # Environment configuration
├── data/            # Data models (Pydantic)
├── core/            # Business logic (email, GitHub)
├── ai/              # AI summarization
├── utils/           # Shared utilities
└── scripts/         # CLI tools
```

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token
- SendGrid API Key
- OpenAI API Key

### Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd engineering-intelligence
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials:
   ```bash
   # GitHub API
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
   GITHUB_REPOS=owner/repo1,owner/repo2
   
   # SendGrid Email
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
   SENDGRID_FROM_EMAIL=noreply@yourcompany.com
   REPORT_RECIPIENT_EMAILS=manager@company.com,team@company.com
   
   # OpenAI API
   OPENAI_API_KEY=sk-xxxxxxxxxxxxx
   OPENAI_MODEL=gpt-4o-mini
   
   # Report Settings
   REPORT_OUTPUT_DIR=./reports
   LOG_LEVEL=INFO
   ```

---

## ⚙️ Configuration

### GitHub Setup

1. Go to https://github.com/settings/tokens
2. Generate a new token with `repo` scope
3. Add to `.env` as `GITHUB_TOKEN`

### SendGrid Setup

1. Create account at https://sendgrid.com
2. Generate API key with "Mail Send" permissions
3. Verify sender email address
4. Add credentials to `.env`

### OpenAI Setup

1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env` as `OPENAI_API_KEY`
3. Model `gpt-4o-mini` is the cheapest option (~$0.15 per 1M tokens)

### Custom AI Prompts

Edit `.env` to customize the AI assistant's personality:

```bash
AI_SYSTEM_PROMPT="You are a helpful engineering assistant for your owner. Provide concise 2-3 line summaries of engineering activity. Be professional but friendly."
AI_MAX_TOKENS=150
AI_TEMPERATURE=0.7
```

---

## 🚀 Usage

### Quick Start (Complete Workflow)

```bash
# 1. Create your weekly report interactively
python scripts/create_projects_json.py

# 2. Preview the email (with AI + GitHub stats)
python scripts/generate_weekly_report.py --input projects.json --dry-run

# 3. Send it!
python scripts/generate_weekly_report.py --input projects.json
```

---

## 📅 Weekly Workflow

### Monday Morning (5 minutes)

#### Option A: Interactive Wizard (Recommended)
```bash
python scripts/create_projects_json.py
```

The wizard will ask:
- Week dates (auto-detected)
- Your name and team
- Each project's status, progress, and blockers
- Overall summary bullets
- Next milestone

#### Option B: Manual Template

Copy `projects_template.json` and fill it out:

```json
{
  "week_start": "2025-10-06",
  "week_end": "2025-10-11",
  "lead_name": "Your Name",
  "team_name": "Product Engineering",
  "projects": [
    {
      "name": "API Platform",
      "status": "on_track",
      "status_text": "On Track",
      "completed": "Auth refactor, rate limiter",
      "in_progress": "Endpoint pagination",
      "blockers": "None",
      "next_week": "Deploy v2.3 to staging"
    }
  ],
  "summary_bullets": [
    "3/4 projects on schedule",
    "Minor delay on frontend"
  ],
  "next_milestone": "Sprint 15 completion",
  "next_milestone_date": "2025-10-18"
}
```

**Status Options:**
- `on_track` → 🟢 Green
- `slight_delay` → 🟡 Yellow
- `ahead` → 🔵 Blue
- `at_risk` → 🔴 Red

### Review and Send

```bash
# Preview first
python scripts/generate_weekly_report.py --input projects.json --dry-run

# Looks good? Send it!
python scripts/generate_weekly_report.py --input projects.json
```

---

## 📖 CLI Reference

### `create_projects_json.py`

Interactive wizard for creating project reports.

```bash
python scripts/create_projects_json.py [OPTIONS]

Options:
  -o, --output PATH       Output file path [default: projects.json]
  --auto-dates           Auto-fill this week's dates [default: True]
  --help                 Show help message
```

**Examples:**
```bash
# Standard usage
python scripts/create_projects_json.py

# Custom output path
python scripts/create_projects_json.py --output reports/week-oct-06.json

# Manually enter dates
python scripts/create_projects_json.py --no-auto-dates
```

---

### `generate_weekly_report.py`

Master script for generating complete reports with AI + GitHub stats.

```bash
python scripts/generate_weekly_report.py [OPTIONS]

Options:
  -i, --input PATH       Path to projects.json file [required]
  --dry-run             Preview email without sending
  --skip-ai             Skip AI summary generation
  --skip-github         Skip GitHub stats collection
  --github-days INT     Days of GitHub history [default: 7]
  --style TEXT          AI style: executive, casual, detailed [default: executive]
  --to TEXT             Override recipients (comma-separated)
  --help                Show help message
```

**Examples:**

```bash
# Full report (AI + GitHub + send)
python scripts/generate_weekly_report.py --input projects.json

# Preview only
python scripts/generate_weekly_report.py --input projects.json --dry-run

# Skip AI intro
python scripts/generate_weekly_report.py --input projects.json --skip-ai

# Skip GitHub stats
python scripts/generate_weekly_report.py --input projects.json --skip-github

# Casual AI tone
python scripts/generate_weekly_report.py --input projects.json --style casual

# Send to different recipients
python scripts/generate_weekly_report.py --input projects.json --to "ceo@company.com,vp@company.com"

# Just projects (no AI, no GitHub)
python scripts/generate_weekly_report.py --input projects.json --skip-ai --skip-github
```

---

### `collect_github_data.py`

Standalone GitHub data collection (for testing or standalone exports).

```bash
python scripts/collect_github_data.py [OPTIONS]

Options:
  -d, --days INT        Number of days of history [default: 7]
  -o, --output PATH     Output JSON file path
  --repos TEXT          Override repos (comma-separated)
  --help                Show help message
```

**Examples:**

```bash
# Collect last 7 days
python scripts/collect_github_data.py --days 7

# Custom output path
python scripts/collect_github_data.py --output reports/github-oct-06.json

# Override repos
python scripts/collect_github_data.py --repos "myorg/repo1,myorg/repo2"

# Collect last 30 days
python scripts/collect_github_data.py --days 30
```

---

### `send_weekly_report.py`

Standalone email sender (for pre-generated reports).

```bash
python scripts/send_weekly_report.py [OPTIONS]

Options:
  -i, --input PATH      Path to projects.json file [required]
  --dry-run            Print email without sending
  --to TEXT            Override recipients
  --help               Show help message
```

---

## 📧 Example Output

### Email Preview

```
Subject: Weekly Engineering Progress – 2025-10-06–2025-10-11 (API Platform, Web Application, Mobile App)

🤖 Hi there! This is Claude, Sebastian's AI assistant. This week showed strong 
momentum with 3/4 projects on track. The API Platform and Mobile App are hitting 
milestones, while the Web Application has a minor delay due to design dependencies.

---

Hi team,

Here's a summary of this week's progress across active projects:

### 1. API Platform
Status: 🟢 On Track
Progress:
- Completed: Authentication refactor, rate limiter, staging fixes
- In Progress: Endpoint pagination, caching optimization
- Blockers: Waiting DB migration window from DevOps
Next Week:
- Deploy v2.3 to staging and start load testing

### 2. Web Application
Status: 🟡 Slight Delay (UI dependency)
Progress:
- Completed: Dashboard backend, notification center
- In Progress: Frontend integration of chart components
- Blockers: Waiting on UI assets from design
Next Week:
- Integrate analytics SDK and finalize responsiveness

### 3. Mobile App
Status: 🟢 On Track
Progress:
- Completed: Login flow, crash reporting, push logic
- In Progress: Offline mode prototype (70%)
- Blockers: None
Next Week:
- Beta testing with internal users

Overall Summary:
- 3/4 projects on or ahead of schedule
- Minor delay on WebApp frontend integration, expected to recover by next sprint
- 💻 Week's Coding: 15 PRs merged, 47 commits across 3 repos

Next Milestone:
- Sprint 15 completion — 2025-10-18

Best,
Sebastian Lee
Lead Software Engineer
(Product Engineering)
```

---

## 🐛 Troubleshooting

### GitHub API Rate Limiting

**Error:** `GitHub API rate limit exceeded`

**Solution:**
- Authenticated requests get 5,000/hour (vs 60/hour unauthenticated)
- Verify your `GITHUB_TOKEN` is set correctly
- Check rate limit: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit`

### SendGrid Authentication Failed

**Error:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**
- Verify API key has "Mail Send" permission
- Check sender email is verified in SendGrid dashboard
- Ensure `SENDGRID_FROM_EMAIL` matches verified sender

### OpenAI API Errors

**Error:** `openai.error.RateLimitError`

**Solutions:**
- Check your OpenAI account has available credits
- Reduce `AI_MAX_TOKENS` in `.env`
- Use `--skip-ai` flag to bypass AI generation

### Module Import Errors

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solutions:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.11+
```

### JSON Validation Errors

**Error:** `Failed to parse report: validation error`

**Solutions:**
- Ensure dates are in `YYYY-MM-DD` format
- Check `status` field uses valid values: `on_track`, `slight_delay`, `ahead`, `at_risk`
- Validate JSON syntax: `python -m json.tool projects.json`

---

## 🧪 Testing

### Test Configuration
```bash
# Verify environment setup
python -c "from config.settings import settings; print('✓ Config loaded')"
```

### Test GitHub Collection
```bash
python scripts/collect_github_data.py --days 1 --output test.json
```

### Test AI Summary
```bash
python -c "
import asyncio
from ai.summarizer import AISummarizer
from data.models import WeeklyReport
from datetime import date

report = WeeklyReport(
    week_start=date(2025,10,6),
    week_end=date(2025,10,11),
    lead_name='Test',
    projects=[]
)

async def test():
    s = AISummarizer()
    result = await s.summarize_weekly_report(report)
    print(result)

asyncio.run(test())
"
```

### Test Email Rendering (Dry Run)
```bash
python scripts/generate_weekly_report.py --input projects.json --dry-run
```

---

## 🔒 Security Best Practices

1. **Never commit `.env`** - It's in `.gitignore` for a reason
2. **Rotate API keys regularly** - Especially if shared with team
3. **Use environment-specific configs** - Different keys for dev/staging/prod
4. **Limit token scopes** - GitHub token only needs `repo` access
5. **Monitor API usage** - Check SendGrid and OpenAI dashboards for anomalies

---

## 🚀 Advanced Usage

### Automation with Cron

Run reports automatically every Friday at 4 PM:

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths)
0 16 * * 5 cd /path/to/project && /path/to/venv/bin/python scripts/generate_weekly_report.py --input projects.json
```

### GitHub Actions Automation

Create `.github/workflows/weekly-report.yml`:

```yaml
name: Weekly Engineering Report

on:
  schedule:
    - cron: '0 16 * * 5'  # Every Friday at 4 PM UTC
  workflow_dispatch: {}

jobs:
  send-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Generate and send report
        env:
          GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
          SENDGRID_FROM_EMAIL: ${{ secrets.SENDGRID_FROM_EMAIL }}
          REPORT_RECIPIENT_EMAILS: ${{ secrets.REPORT_RECIPIENT_EMAILS }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python scripts/generate_weekly_report.py --input projects.json
```

### Custom Email Templates

Create HTML email renderer in `core/email_renderer.py`:

```python
class HTMLEmailRenderer:
    """Renders reports as HTML emails with custom styling."""
    
    def render(self, report: WeeklyReport) -> tuple[str, str]:
        # Your HTML template logic here
        pass
```

---

## 📚 API Reference

### Core Classes

#### `WeeklyReport` (data/models.py)
Main data model for project reports.

```python
from data.models import WeeklyReport, ProjectUpdate, ProjectStatus

report = WeeklyReport(
    week_start=date(2025, 10, 6),
    week_end=date(2025, 10, 11),
    lead_name="Your Name",
    team_name="Engineering",
    projects=[...],
    summary_bullets=[...],
    next_milestone="Sprint 15",
    next_milestone_date=date(2025, 10, 18)
)
```

#### `AISummarizer` (ai/summarizer.py)
Generates AI-powered summaries.

```python
from ai.summarizer import AISummarizer

summarizer = AISummarizer(
    model="gpt-4o-mini",
    system_prompt="Custom prompt...",
    max_tokens=150,
    temperature=0.7
)

summary = await summarizer.summarize_weekly_report(report, style="executive")
```

#### `GitHubCollector` (core/github_collector.py)
Collects GitHub activity data.

```python
from core.github_collector import GitHubCollector
from datetime import datetime, timedelta

collector = GitHubCollector(
    access_token="ghp_xxx",
    repos=["owner/repo1", "owner/repo2"]
)

report = collector.collect_activity(
    since=datetime.utcnow() - timedelta(days=7),
    until=datetime.utcnow()
)
```

#### `EmailSender` (core/email_sender.py)
Sends emails via SendGrid.

```python
from core.email_sender import EmailSender

sender = EmailSender(
    api_key="SG.xxx",
    from_email="noreply@company.com"
)

await sender.send_email(
    to_emails=["recipient@company.com"],
    subject="Weekly Report",
    body="Report content..."
)
```

---

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install black ruff mypy pytest pytest-asyncio

# Run code formatting
black .

# Run linting
ruff check .

# Run type checking
mypy .

# Run tests
pytest
```

### Code Style

- Follow PEP 8
- Use type hints everywhere
- Document all public APIs
- Write descriptive commit messages

---

## 📄 License

Proprietary - Internal Use Only

---

## 💬 Support

For questions or issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in console output
3. Open an issue in the repository

---

## 🎉 Acknowledgments

Built with:
- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API wrapper
- [OpenAI](https://openai.com) - AI summarization
- [SendGrid](https://sendgrid.com) - Email delivery
- [Pydantic](https://pydantic.dev) - Data validation
- [Typer](https://typer.tiangolo.com) - CLI framework
- [Rich](https://rich.readthedocs.io) - Terminal formatting

---

**Happy Reporting! 🚀**
```

---

## 🎉 DONE!

You now have:
- ✅ Complete, production-ready codebase
- ✅ Full documentation with examples
- ✅ Interactive CLI tools
- ✅ AI-powered summaries
- ✅ GitHub integration
- ✅ Email delivery
- ✅ Troubleshooting guide
- ✅ API reference

> **Your system is ready to use! Start with `python scripts/create_projects_json.py` and let me know how it goes! 🚀**