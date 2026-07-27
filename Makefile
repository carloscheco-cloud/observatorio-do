PYTHON ?= python

.PHONY: install lint format typecheck test test-integration db-up db-down migrate seed run check frontend-install frontend-dev frontend-lint frontend-typecheck frontend-test frontend-build stack
install:
	$(PYTHON) -m pip install -e ".[dev]"
lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .
format:
	$(PYTHON) -m ruff format .
typecheck:
	$(PYTHON) -m mypy
test:
	$(PYTHON) -m pytest -m "not integration"
test-integration:
	$(PYTHON) -m pytest -m integration
db-up:
	docker compose up -d db
db-down:
	docker compose down
migrate:
	cd backend && $(PYTHON) -m alembic upgrade head
seed:
	cd backend && $(PYTHON) -m app.db.seed
run:
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload
check: lint typecheck test
frontend-install:
	cd frontend && npm ci
frontend-dev:
	cd frontend && npm run dev
frontend-lint:
	cd frontend && npm run lint
frontend-typecheck:
	cd frontend && npm run typecheck
frontend-test:
	cd frontend && npm test
frontend-build:
	cd frontend && npm run build
stack:
	docker compose up --build

