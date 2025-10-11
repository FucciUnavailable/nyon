.PHONY: build run create collect clean help

# Variables
IMAGE_NAME = engineering-intelligence
TAG = latest

help: ## Show this help message
	@echo "Engineering Intelligence - Docker Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker image
	docker build -t $(IMAGE_NAME):$(TAG) .

run: ## Generate and send weekly report
	docker-compose run --rm weekly-report

create: ## Run interactive wizard to create projects.json
	docker-compose run --rm create-report

collect: ## Collect GitHub data only
	docker-compose run --rm collect-github

dry-run: ## Preview report without sending
	docker-compose run --rm weekly-report python scripts/generate_weekly_report.py --input projects.json --dry-run

shell: ## Open shell in container
	docker-compose run --rm weekly-report /bin/bash

clean: ## Remove containers and images
	docker-compose down
	docker rmi $(IMAGE_NAME):$(TAG)

logs: ## View logs
	docker-compose logs -f

.DEFAULT_GOAL := help