# Keitaro Campaign Tool — GRACE 4 Engineering Protocol

## Keywords

keitaro, campaign, stream, offer, share, fastapi, sqlalchemy, alembic, react, fsd, tanstack-query, shadcn, grace

## Annotation

Test assignment (Adrobot): a FastAPI + SQLAlchemy backend and a React (Feature-Sliced Design) frontend over the Keitaro Admin API. Two features: a **campaign creator** (name + geo + offer → campaign with domain, group, source and two streams: geo → Google, everyone else → offer) and an **offer editor** for existing campaigns (add / remove offers, shares, stats).

## Repository Map

| Path | What |
| --- | --- |
| `apps/backend` | FastAPI app (`app/`), Alembic (`alembic/`), contract export (`scripts/`). uv-managed. |
| `apps/frontend` | React 19 + Vite + TanStack Query + Tailwind 4 + shadcn/ui, FSD layers under `src/`. npm-managed. |
| `contracts/openapi.json` | The public HTTP API contract, exported from the backend. |
| `.grace/` | GRACE 4 normative state: context, graph, verification, changes. |
| `.claude/skills/grace-*`, `.claude/agents/grace-*` | GRACE skills and worker/reviewer subagent presets. |
| `Makefile` | Run targets and **all verification gates**. |

## Sources of Truth

`.grace/` is **normative**: intent, approved scope, lifecycle state, verification obligation. The code is **observational**.

| To learn | Read |
| --- | --- |
| Product and technical context, decisions | `.grace/context/*.xml` (`requirements.xml` → `Decisions`) |
| Which module owns a file | `.grace/graph/index.xml` → `graph/main.xml` (`<Path>` entries) |
| What must be proven and by which gate | `.grace/verification/index.xml` → `verification/main.xml` |
| What is approved and in progress | `.grace/changes/active/C-*/spec.xml`, `plan.xml` |
| How a past change was decided | `.grace/changes/archive/C-*/` |
| Whether work is complete | fresh output of the plan's `TargetAssertions` commands |

Within a change bundle `spec.xml` is normative, `design-context.xml` is explanatory.

## Hard Rules

1. **Tests are banned.** Never add a test file, test framework (pytest, vitest, jest, playwright…), test target, coverage config or a verification command that runs tests. Never propose one. When something needs proof, use the strongest existing gate (below) and, where nothing can machine-check it, record a review obligation as a `TraceAssertion` in the owning `V-M-*`.
2. **Every API contract change goes through GRACE.** The API contract is `contracts/openapi.json`, owned by `M-API-CONTRACT` and produced by `M-BACKEND-API` (`app/api/**`, `app/schemas/**`, `app/main.py`). Any change that alters routes, params, request/response models, status codes or `operation_id`s requires: `grace-spec` → approved `spec.xml` → `grace-plan` → approved `plan.xml` → `grace-execute`. The change must regenerate the contract and TS types with `make openapi` and pass `make gate-openapi`. No exceptions for "small" API changes.
3. **Other behaviour changes** (backend services, DB schema / migrations, Keitaro integration, infra) also go through a GRACE change bundle.
4. **Small UI changes may skip the bundle**: copy, styling, layout, spacing, icons, purely presentational component tweaks in `apps/frontend/src/**` that do not change API usage or data flow. Make the edit, keep file-local markup valid, run `make gate-frontend` and `grace lint --path . --failOn errors`, and name the lifecycle step you bypassed in the handoff. New FSD slices, new queries/mutations or changed data flow are **not** small.
5. **Secrets**: the Keitaro API key lives only in the root `.env` (gitignored; template `.env.example`). Never put it in tracked files, the frontend, logs or the contract.
6. **Never hand-edit generated files**: `contracts/openapi.json`, `apps/frontend/src/shared/api/schema.d.ts` (run `make openapi`), `apps/frontend/src/shared/ui/*` come from shadcn (edit only to fix imports/theme).
7. Do not commit, push or create PRs unless the user asks.

## Working a Change (GRACE)

1. **Orient.** Read `.grace/context/`, the routed graph document for the affected module, the routed verification document, and the change's `spec.xml` + `plan.xml`. Then read the code they point at, narrowing with file-local `LINKS:` and `START_BLOCK_` anchors. Use `grace module find|show`, `grace file show`, `grace verification show`.
2. **Confirm it is executable.** Implement only with an approved spec **and** an approved plan (except rule 4). `ObservedWriteScope` is the boundary of the work.
3. **Implement.** Know which `M-*` / `V-M-*` owns each file before editing. Keep `START_MODULE_CONTRACT` / `START_MODULE_MAP` / `LINKS` blocks in every governed file; `START_MODULE_MAP` lists **every** exported top-level symbol, one per line (`name - purpose`). Add `START_CONTRACT:` for public functions with side effects and `START_BLOCK_*` around critical sections; log lines inside a block use the `[Module][function][BLOCK_NAME]` prefix.
4. **Markup gate after each task (hard stop):**
   ```
   grace lint --path . --failOn errors
   grace status --path . --json | jq -e '.observedDrift.unexplainedFiles | length == 0'
   ```
   Leave observed writes uncommitted until the change is applied, otherwise the drift check cannot see them.
5. **Verify** with the plan's `TargetAssertions` and the owning `V-M-*` commands; quote real output and exit codes. Never report a gate that did not run.
6. **Report drift**: every touched file must sit under a `<Path>` of a module in `AffectedAreas`; otherwise it is a required graph delta.
7. **Apply** only after explicit user confirmation: set spec/plan `status="applied"`, move the bundle to `.grace/changes/archive/`.

## Verification Gates

| Gate | Covers |
| --- | --- |
| `make gate-backend` | `ruff check`, `ruff format --check`, `mypy --strict` in `apps/backend` |
| `make gate-frontend` | `oxlint`, `steiger` (FSD rules), `tsc -b`, `vite build` in `apps/frontend` |
| `make gate-openapi` | code ↔ `contracts/openapi.json` ↔ `schema.d.ts` drift |
| `make gate-compose` | `docker compose config -q` |
| `make gate` | all of the above |
| `grace lint --path . --failOn errors` | `.grace` grammar, projections, markup, scopes |

## Backend Architecture (apps/backend/app)

Layered, dependencies point downward only:

```
api/routes/*  (HTTP: parse, call service, return DTO)        M-BACKEND-API
schemas/*     (pydantic DTOs = API contract)                  M-BACKEND-API
services/*    (business rules: creator, editor, shares)       M-CAMPAIGN-CREATOR, M-OFFER-EDITOR
integrations/keitaro/* (HTTP client + wire models)            M-KEITARO-CLIENT
models/*, db/* (SQLAlchemy ORM, session) + alembic/           M-DB
core/*        (settings, errors)                              M-BACKEND-CORE
```

- Routes contain no business logic; services never import FastAPI routing.
- DB schema changes = new Alembic revision in `alembic/versions/` (never edit an applied one).
- Errors: raise `NotFoundError` / `ValidationFailedError` / `UpstreamError` from `app.core.errors`.

## Frontend Architecture (apps/frontend/src) — Feature-Sliced Design

Layers (import only from layers below): `app → pages → widgets → features → entities → shared`.

- Each slice exposes a public API via `index.ts`; import other slices only through it (`@/features/add-offer`, never `@/features/add-offer/ui/...`).
- Server state lives in TanStack Query hooks (`entities/*/api`, `features/*/model`); mutations invalidate `campaignKeys`.
- HTTP only through `@/shared/api` (`api` + `unwrap`), typed by generated `schema.d.ts`.
- UI primitives from shadcn in `@/shared/ui`; Russian UI copy.
- `steiger src` must pass (part of `npm run lint`).

## Subagents

| Subagent | Delegate when |
| --- | --- |
| `grace-worker` | implementing a task of an approved plan while you keep the gates and `.grace` edits |
| `grace-reviewer` | before asking for apply confirmation on a change that touches code |

If subagents are unavailable, do the work yourself.
