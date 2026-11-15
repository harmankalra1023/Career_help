.PHONY: help dev test lint format migrate seed clean docker-build

help:
	@echo "Digital Career Twin (DCT) - Development Commands"
	@echo "==============================================="
	@echo "make dev           - Start full stack in Docker (or local dev)"
	@echo "make test          - Run backend & frontend test suites"
	@echo "make lint          - Run linters (ruff, mypy, eslint)"
	@echo "make format        - Auto-format codebases"
	@echo "make migrate       - Run database migrations (Alembic)"
	@echo "make seed          - Seed taxonomy, roles, and reference data"
	@echo "make clean         - Clean temporary caches and artifacts"

dev:
	docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml up --build

dev-backend:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd apps/web && npm run dev

test: test-backend test-frontend

test-backend:
	cd apps/api && pytest -v

test-frontend:
	cd apps/web && npm test

lint: lint-backend lint-frontend

lint-backend:
	cd apps/api && ruff check . && mypy app

lint-frontend:
	cd apps/web && npm run lint

format:
	cd apps/api && ruff format .
	cd apps/web && npm run format

migrate:
	cd apps/api && alembic upgrade head

seed:
	cd apps/api && python -m app.db.seed

docker-build:
	docker compose -f deploy/docker-compose.yml build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +
