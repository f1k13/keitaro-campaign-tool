# START_MODULE_CONTRACT
#   PURPOSE: Developer entrypoints and verification gates (tests are banned; gates are static).
#   SCOPE: run, migrate, OpenAPI contract export, gate-* targets.
#   DEPENDS: none
#   LINKS: M-INFRA, V-M-INFRA
# END_MODULE_CONTRACT
.PHONY: up down logs db migrate backend frontend openapi api-types gate gate-backend gate-frontend gate-openapi gate-compose

BACKEND := apps/backend
FRONTEND := apps/frontend

up:            ## full stack in Docker: http://localhost:8080
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f backend

db:            ## only PostgreSQL (for local dev)
	docker compose up -d db

migrate:       ## apply Alembic migrations to local DB
	cd $(BACKEND) && uv run alembic upgrade head

backend:       ## FastAPI dev server with reload on :8000
	cd $(BACKEND) && uv run uvicorn app.main:app --reload --port 8000

frontend:      ## Vite dev server on :5173 (proxies /api to :8000)
	cd $(FRONTEND) && npm run dev

openapi:       ## regenerate contracts/openapi.json and frontend API types
	cd $(BACKEND) && uv run python -m scripts.export_openapi
	$(MAKE) api-types

api-types:
	cd $(FRONTEND) && npx openapi-typescript ../../contracts/openapi.json -o src/shared/api/schema.d.ts

gate: gate-backend gate-frontend gate-openapi gate-compose

gate-backend:  ## ruff + format check + mypy
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check . && uv run mypy .

gate-frontend: ## oxlint + tsc + vite build
	cd $(FRONTEND) && npm run lint && npm run build

gate-openapi:  ## contract drift: code vs contracts/openapi.json vs generated TS types
	cd $(BACKEND) && uv run python -m scripts.export_openapi --check
	cd $(FRONTEND) && npx openapi-typescript ../../contracts/openapi.json -o /tmp/schema.check.d.ts >/dev/null && diff -q /tmp/schema.check.d.ts src/shared/api/schema.d.ts

gate-compose:  ## compose file validity
	docker compose config -q
