# Keitaro Campaign Tool

Тестовое задание Adrobot. Это инструмент поверх Keitaro Admin API из двух частей.

1. **Создаватор кампаний.** На вход: название, гео (ISO-код страны) и ID оффера. Создаётся кампания с доменом, группой и источником, в ней два потока:
   - поток №1 (перехват): фильтр `country = <гео>` → редирект на `https://www.google.com`;
   - поток №2 (обычный, «лендинги и офферы»): весь остальной трафик → выбранный оффер (100%).
2. **Редактор офферов существующей кампании.** Показывает потоки кампании, офферы в них с долями и статистикой (клики, конверсии, CR, доход, EPC, прибыль за выбранный период). Умеет:
   - **добавить** оффер: доли всех активных офферов пересчитываются поровну (100 → 50/50 → 34/33/33);
   - **удалить** оффер (с подтверждением): оставшиеся активные офферы снова делятся поровну;
   - **поправить доли вручную** и включить или выключить оффер. Сумма долей активных офферов обязана быть 100%, иначе бэкенд вернёт 422 и в Keitaro ничего не уйдёт.

Каждое изменение офферов записывается в журнал (PostgreSQL) со снимком «было / стало». Созданные кампании тоже сохраняются в БД.

## Стек

| | |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2 (async, asyncpg), Alembic, httpx, pydantic-settings, uv |
| Frontend | React 19, Vite, TypeScript, TanStack Query, Tailwind CSS 4, shadcn/ui, Feature-Sliced Design, openapi-fetch |
| Инфра | PostgreSQL 17, Docker Compose, nginx |
| Процесс | [GRACE 4](https://github.com/osovv/grace-marketplace): `.grace/`, skills в `.claude/skills` |

```
apps/
  backend/     FastAPI + SQLAlchemy + Alembic
  frontend/    React + Vite (FSD)
contracts/
  openapi.json контракт API (генерируется из бэкенда)
.grace/        GRACE: контекст, граф модулей, verification, изменения
```

## Быстрый старт (Docker)

```bash
cp .env.example .env
# вписать KEITARO_BASE_URL, KEITARO_API_KEY, ID домена, группы и источника по умолчанию
# и CAMPAIGN_NAME_PREFIX (например test_ivanov_)
make up            # = docker compose up --build -d
```

- UI: http://localhost:8080
- API и Swagger: http://localhost:8000/docs

Миграции применяются автоматически при старте контейнера `backend` (`alembic upgrade head`).

Все настройки лежат в одном файле `.env` в корне репозитория. Его читают и docker compose, и бэкенд при локальном запуске.

## Локальная разработка

Нужны [uv](https://docs.astral.sh/uv/) (он сам поставит Python 3.13), Node 22+ и Docker (для Postgres).

```bash
make db                              # Postgres в Docker на localhost:5433
cd apps/backend && uv sync && cd -   # зависимости бэкенда (.venv)
make migrate                         # alembic upgrade head
make backend                         # FastAPI на :8000 (reload)

cd apps/frontend && npm install && cd -
make frontend                        # Vite на :5173, /api проксируется на :8000
```

### Миграции

```bash
cd apps/backend
uv run alembic upgrade head                            # применить
uv run alembic revision --autogenerate -m "описание"   # новая миграция после правки models/
uv run alembic downgrade -1                            # откатить последнюю
```

Таблицы:

- `created_campaigns`: кампании, созданные через инструмент;
- `offer_changes`: журнал изменений офферов в потоках.

### Контракт API

После любого изменения роутов или схем:

```bash
make openapi       # обновит contracts/openapi.json и apps/frontend/src/shared/api/schema.d.ts
```

## Проверки (гейты)

Тестов в проекте нет намеренно, это правило проекта. Корректность подтверждают статические гейты:

```bash
make gate          # всё сразу
make gate-backend  # ruff + ruff format --check + mypy --strict
make gate-frontend # oxlint + steiger (FSD) + tsc + vite build
make gate-openapi  # код ↔ contracts/openapi.json ↔ TS-типы
make gate-compose  # docker compose config
grace lint --path . --failOn errors   # GRACE-артефакты и разметка кода
```

## API

| Метод | Путь | Что делает |
|---|---|---|
| GET | `/api/reference/offers` \| `domains` \| `groups` \| `traffic-sources` \| `defaults` | справочники для формы |
| POST | `/api/campaigns` | создать кампанию `{name, country, offer_id, domain_id?, group_id?, traffic_source_id?}`; к имени добавляется `CAMPAIGN_NAME_PREFIX` |
| GET | `/api/campaigns?search=` | кампании из Keitaro (для выбора в редакторе) |
| GET | `/api/campaigns/created` | история созданных кампаний |
| GET | `/api/campaigns/{id}/editor?interval=` | потоки, офферы, доли и статистика |
| POST | `/api/campaigns/{id}/streams/{sid}/offers` | добавить оффер `{offer_id}` |
| DELETE | `/api/campaigns/{id}/streams/{sid}/offers/{offer_id}` | удалить оффер |
| PUT | `/api/campaigns/{id}/streams/{sid}/offers` | задать доли вручную `{offers:[{offer_id, share, state}]}` |
| GET | `/api/campaigns/{id}/changes` | журнал изменений |

## Допущения

- Видео с эталонным редактором автору недоступно. Правило долей («при добавлении или удалении делим поровну, вручную можно править, но сумма 100») записано в `.grace/context/requirements.xml` → `Decisions`.
- API-ключ в тестовом трекере видит только часть офферов. Поэтому в редакторе оффер можно добавить и по ID вручную.

## Разработка с агентами (GRACE)

Правила для агентов лежат в [`AGENTS.md`](AGENTS.md) (`CLAUDE.md` — симлинк на него). Коротко:

- тесты не пишем;
- любое изменение контракта API и поведения проходит через `grace-spec` → `grace-plan` → `grace-execute`;
- мелкие правки UI можно делать напрямую.

CLI GRACE: `bun add -g @osovv/grace-cli`.
