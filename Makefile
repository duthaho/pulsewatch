.PHONY: help setup run test lint format clean migrate docker-up docker-down docker-build docker-logs docker-shell check

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Initial project setup (venv, dependencies, pre-commit)
	python3.12 -m venv venv
	. venv/bin/activate && pip install -r requirements/dev.txt
	pre-commit install
	cp .env.example .env
	@echo "Setup complete! Edit .env and run 'make migrate' to initialize database"

run:  ## Run development server locally
	python manage.py runserver

docker-up:  ## Start all services with Docker Compose
	docker-compose up -d
	@echo "Services started! Web: http://localhost:8000"

docker-down:  ## Stop and remove Docker containers
	docker-compose down

docker-build:  ## Build Docker images
	docker-compose build

docker-logs:  ## View Docker logs (all services)
	docker-compose logs -f

docker-shell:  ## Open bash shell in web container
	docker-compose exec web bash

migrate:  ## Run database migrations
	python manage.py migrate

makemigrations:  ## Create new migrations
	python manage.py makemigrations

test:  ## Run test suite with coverage
	pytest --cov --cov-report=term-missing --cov-report=html

test-unit:  ## Run unit tests only
	pytest tests/unit/

test-integration:  ## Run integration tests only
	pytest tests/integration/

test-contract:  ## Run contract tests only
	pytest tests/contract/

lint:  ## Run all linters (check only)
	black --check .
	isort --check .
	flake8 .
	mypy .

format:  ## Auto-format code (black, isort)
	black .
	isort .

check:  ## Run all quality checks (lint + test)
	make lint
	make test

clean:  ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	rm -rf build dist *.egg-info

superuser:  ## Create Django superuser
	python manage.py createsuperuser

shell:  ## Open Django shell
	python manage.py shell

dbshell:  ## Open database shell
	python manage.py dbshell

install:  ## Install dependencies
	pip install -r requirements/dev.txt

install-prod:  ## Install production dependencies only
	pip install -r requirements/prod.txt

collectstatic:  ## Collect static files
	python manage.py collectstatic --noinput

health:  ## Check health endpoints
	@echo "Checking /healthz..."
	@curl -s http://localhost:8000/healthz | python -m json.tool || echo "Failed"
	@echo "\nChecking /ready..."
	@curl -s http://localhost:8000/ready | python -m json.tool || echo "Failed"

metrics:  ## View Prometheus metrics
	@curl -s http://localhost:8000/metrics | head -n 50

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

update-deps:  ## Update pre-commit hooks and Python dependencies
	pre-commit autoupdate
	pip list --outdated
