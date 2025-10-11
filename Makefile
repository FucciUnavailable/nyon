.PHONY: help install dev test lint format type-check clean run-local run-docker build-docker

# Variables
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin
DOCKER_IMAGE := engineering-intelligence
DOCKER_TAG := latest

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[36m

##@ Help

help: ## Show this help message
	@echo "$(COLOR_BOLD)Engineering Intelligence - Available Commands$(COLOR_RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(COLOR_BLUE)%-20s$(COLOR_RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(COLOR_BOLD)%s$(COLOR_RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

install: ## Install dependencies in virtual environment
	@echo "$(COLOR_GREEN)Creating virtual environment...$(COLOR_RESET)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(COLOR_GREEN)Installing dependencies...$(COLOR_RESET)"
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "$(COLOR_GREEN)✓ Installation complete!$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Run 'source $(VENV)/bin/activate' to activate$(COLOR_RESET)"

install-dev: install ## Install with development dependencies
	@echo "$(COLOR_GREEN)Installing dev dependencies...$(COLOR_RESET)"
	$(BIN)/pip install black ruff mypy pytest pytest-asyncio
	@echo "$(COLOR_GREEN)✓ Dev dependencies installed!$(COLOR_RESET)"

setup: install ## Complete first-time setup
	@echo "$(COLOR_GREEN)Creating .env file...$(COLOR_RESET)"
	@if [ ! -f .env ]; then cp .env.example .env; echo "$(COLOR_YELLOW)⚠ Edit .env and add your API keys!$(COLOR_RESET)"; else echo ".env already exists"; fi
	@echo "$(COLOR_GREEN)Creating reports directory...$(COLOR_RESET)"
	@mkdir -p reports
	@echo "$(COLOR_GREEN)✓ Setup complete!$(COLOR_RESET)"

##@ Development

dev: ## Activate virtual environment (instructions)
	@echo "$(COLOR_YELLOW)Run this command:$(COLOR_RESET)"
	@echo "  source $(VENV)/bin/activate"

test: ## Run tests
	@echo "$(COLOR_GREEN)Running tests...$(COLOR_RESET)"
	$(BIN)/pytest -v

test-cov: ## Run tests with coverage
	@echo "$(COLOR_GREEN)Running tests with coverage...$(COLOR_RESET)"
	$(BIN)/pytest --cov=. --cov-report=html --cov-report=term

lint: ## Run linter (ruff)
	@echo "$(COLOR_GREEN)Running linter...$(COLOR_RESET)"
	$(BIN)/ruff check .

format: ## Format code with black
	@echo "$(COLOR_GREEN)Formatting code...$(COLOR_RESET)"
	$(BIN)/black .

format-check: ## Check if code needs formatting
	@echo "$(COLOR_GREEN)Checking code formatting...$(COLOR_RESET)"
	$(BIN)/black --check .

type-check: ## Run type checker (mypy)
	@echo "$(COLOR_GREEN)Running type checker...$(COLOR_RESET)"
	$(BIN)/mypy .

check: format-check lint type-check ## Run all checks (format, lint, type)

##@ Running Locally (Without Docker)

create-local: ## Create projects.json interactively (local)
	@echo "$(COLOR_GREEN)Starting interactive wizard...$(COLOR_RESET)"
	$(BIN)/python scripts/create_projects_json.py

preview-local: ## Preview report without sending (local)
	@echo "$(COLOR_GREEN)Previewing report...$(COLOR_RESET)"
	$(BIN)/python scripts/generate_weekly_report.py --input projects.json --dry-run

send-local: ## Generate and send report (local)
	@echo "$(COLOR_GREEN)Generating and sending report...$(COLOR_RESET)"
	$(BIN)/python scripts/generate_weekly_report.py --input projects.json

send-local-no-ai: ## Send report without AI summary (local)
	@echo "$(COLOR_GREEN)Sending report (no AI)...$(COLOR_RESET)"
	$(BIN)/python scripts/generate_weekly_report.py --input projects.json --skip-ai

send-local-no-github: ## Send report without GitHub stats (local)
	@echo "$(COLOR_GREEN)Sending report (no GitHub)...$(COLOR_RESET)"
	$(BIN)/python scripts/generate_weekly_report.py --input projects.json --skip-github

collect-github-local: ## Collect GitHub data (local)
	@echo "$(COLOR_GREEN)Collecting GitHub data...$(COLOR_RESET)"
	$(BIN)/python scripts/collect_github_data.py --days 7

##@ Docker Operations

build-docker: ## Build Docker image
	@echo "$(COLOR_GREEN)Building Docker image...$(COLOR_RESET)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

build: build-docker ## Alias for build-docker

create-docker: ## Create projects.json interactively (Docker)
	@echo "$(COLOR_GREEN)Starting interactive wizard (Docker)...$(COLOR_RESET)"
	docker-compose run --rm create-report

preview-docker: ## Preview report without sending (Docker)
	@echo "$(COLOR_GREEN)Previewing report (Docker)...$(COLOR_RESET)"
	docker-compose run --rm weekly-report python scripts/generate_weekly_report.py --input projects.json --dry-run

send-docker: ## Generate and send report (Docker)
	@echo "$(COLOR_GREEN)Generating and sending report (Docker)...$(COLOR_RESET)"
	docker-compose run --rm weekly-report

collect-github-docker: ## Collect GitHub data (Docker)
	@echo "$(COLOR_GREEN)Collecting GitHub data (Docker)...$(COLOR_RESET)"
	docker-compose run --rm collect-github

shell-docker: ## Open shell in Docker container
	@echo "$(COLOR_GREEN)Opening shell in container...$(COLOR_RESET)"
	docker-compose run --rm weekly-report /bin/bash

##@ Quick Workflows

create: create-local ## Quick: Create projects.json (local by default)

preview: preview-local ## Quick: Preview report (local by default)

send: send-local ## Quick: Send report (local by default)

workflow: create preview ## Quick: Create + Preview

workflow-send: create send ## Quick: Create + Send (be careful!)

##@ Cleanup

clean: ## Remove Python cache and build artifacts
	@echo "$(COLOR_GREEN)Cleaning Python cache...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(COLOR_GREEN)✓ Cleaned!$(COLOR_RESET)"

clean-venv: clean ## Remove virtual environment
	@echo "$(COLOR_GREEN)Removing virtual environment...$(COLOR_RESET)"
	rm -rf $(VENV)
	@echo "$(COLOR_GREEN)✓ Virtual environment removed!$(COLOR_RESET)"

clean-docker: ## Remove Docker containers and images
	@echo "$(COLOR_GREEN)Removing Docker containers and images...$(COLOR_RESET)"
	docker-compose down
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	@echo "$(COLOR_GREEN)✓ Docker cleaned!$(COLOR_RESET)"

clean-all: clean-venv clean-docker ## Remove everything (venv + docker)
	@echo "$(COLOR_GREEN)Removing reports...$(COLOR_RESET)"
	rm -rf reports/*
	@echo "$(COLOR_GREEN)✓ Everything cleaned!$(COLOR_RESET)"

##@ CI/CD Helpers

ci-install: ## Install dependencies for CI
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install black ruff mypy pytest pytest-asyncio

ci-test: check test ## Run all CI checks and tests

##@ Utilities

validate-env: ## Check if .env file has all required variables
	@echo "$(COLOR_GREEN)Validating .env file...$(COLOR_RESET)"
	@$(BIN)/python -c "from config.settings import settings; print('✓ Configuration valid!')"

show-config: ## Display current configuration (without secrets)
	@echo "$(COLOR_GREEN)Current Configuration:$(COLOR_RESET)"
	@$(BIN)/python -c "from config.settings import settings; print(f'Repos: {settings.get_repos_list()}'); print(f'Recipients: {settings.get_recipients_list()}'); print(f'Model: {settings.openai_model}'); print(f'Output Dir: {settings.report_output_dir}')"

logs: ## Show recent logs from reports
	@echo "$(COLOR_GREEN)Recent logs:$(COLOR_RESET)"
	@tail -n 50 reports/*.log 2>/dev/null || echo "No logs found"

version: ## Show version info
	@echo "$(COLOR_BOLD)Engineering Intelligence System$(COLOR_RESET)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Venv: $(shell test -d $(VENV) && echo 'Active' || echo 'Not installed')"
	@echo "Docker: $(shell docker --version 2>/dev/null || echo 'Not installed')"

.DEFAULT_GOAL := help