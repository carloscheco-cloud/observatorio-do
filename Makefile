PYTHON ?= python

.PHONY: install lint format typecheck test test-integration db-up db-down migrate seed run check
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

