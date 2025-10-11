
markdown## 🐳 Docker Usage

### Quick Start with Docker
```bash
# Build image
docker-compose build

# Create weekly report
docker-compose run --rm create-report

# Send report
docker-compose run --rm weekly-report

# Preview without sending
docker-compose run --rm weekly-report \
  python scripts/generate_weekly_report.py --input projects.json --dry-run
Using Makefile (Recommended)
bashmake build      # Build Docker image
make create     # Create projects.json
make dry-run    # Preview report
make run        # Send report
make help       # Show all commands
Run from Anywhere
Add to ~/.bashrc:
bashalias ei-send='docker run --rm --env-file ~/.config/ei/.env -v ~/projects.json:/app/projects.json:ro engineering-intelligence:latest python scripts/generate_weekly_report.py --input projects.json'
Then from anywhere:
bashei-send
Without Docker Compose
bash# Build
docker build -t engineering-intelligence:latest .

# Run
docker run --rm \
  --env-file .env \
  -v $(pwd)/projects.json:/app/projects.json:ro \
  -v $(pwd)/reports:/app/reports \
  engineering-intelligence:latest \
  python scripts/generate_weekly_report.py --input projects.json