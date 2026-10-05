SHELL := /bin/bash
COMPOSE := docker compose

-include .env
export
API_PORT ?= 8000
APP_PORT ?= 8080

STACK := scripts/stack

.PHONY: help setup dev gen check check-backend check-frontend up down logs reseed \
	stack-lease stack-release template-refresh

help:
	@grep -E '^## ' Makefile | sed 's/^## //'

## setup   install backend + frontend deps, create .env
## dev     db + redis in Docker; api, worker, web with hot reload
## gen     regenerate openapi.json and the typed TS client
## check   stack infra ensure, then check-backend + check-frontend
## check-backend   lint, format, typecheck, tests in this slot's test DB (never calls compose)
## check-frontend  lint, typecheck, tests (never calls compose)
## up      prod-like stack in Docker (2 workers), web on APP_PORT   [human]
## down    stop the prod-like stack                                  [human]
## logs    follow prod-like stack logs
## reseed  reset and reseed demo data (in the slot's app_sN when .env.slot exists)
## stack-lease OWNER=me    lease a slot for this worktree (writes .env.slot)
## stack-release [SLOT=N]  drop the slot's DBs and free it (default: this worktree's slot)
## template-refresh        rebuild app_template (migrate + reseed) at this checkout's head
## (dev, up, down are human commands; agents use scripts/stack, see CLAUDE.md)

setup:
	cd backend && uv sync --frozen
	cd frontend && npm ci
	test -f .env || cp .env.example .env

dev:
	$(COMPOSE) up -d --wait db redis
	cd backend && uv run alembic upgrade head
	trap 'kill 0' INT TERM EXIT; \
	(cd backend && uv run uvicorn app.api.main:app --reload --host 127.0.0.1 --port $(API_PORT)) & \
	(cd backend && uv run watchfiles --filter python "celery -A app.worker.celery_app worker -Q default,llm --pool=solo --loglevel=INFO" app) & \
	(cd frontend && npm run dev) & \
	wait

gen:
	cd backend && uv run python -m app.export_openapi
	cd frontend && npm run gen

check:
	$(STACK) infra ensure
	$(MAKE) check-backend check-frontend

check-backend:
	cd backend && uv run ruff check . ../scripts && uv run ruff format --check . ../scripts \
		&& uv run mypy app tests ../scripts/stack.py
	$(STACK) run --db test --heavy -- bash -c 'cd backend && uv run pytest -q'

check-frontend:
	cd frontend && npm run lint && npm run typecheck && npm test

up:
	$(COMPOSE) --profile app up -d --build --scale worker=2
	for i in $$(seq 1 60); do curl -sf localhost:$(API_PORT)/ready && echo && exit 0; sleep 1; done; exit 1

down:
	$(COMPOSE) --profile app down

logs:
	$(COMPOSE) --profile app logs -f --tail=50

reseed:
	if [ -f .env.slot ]; then \
		$(STACK) run --db dev --heavy -- bash -c 'cd backend && uv run alembic upgrade head && uv run python scripts/reseed.py'; \
	else \
		cd backend && uv run alembic upgrade head && uv run python scripts/reseed.py; \
	fi

stack-lease:
	$(STACK) lease $(or $(OWNER),$(USER))

stack-release:
	$(STACK) release $(SLOT)

template-refresh:
	$(STACK) template refresh
