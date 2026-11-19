# Keitaro Campaign Tool

Тестовое задание Adrobot. Это инструмент поверх Keitaro Admin API из двух частей.

1. **Создаватор кампаний.** На вход: название, гео (ISO-код страны) и ID оффера. Создаётся кампания с доменом, группой и источником, в ней два потока:
   - поток №1 (перехват): фильтр `country = <гео>` → редирект на `https://www.google.com`;
   - поток №2 (обычный, «лендинги и офферы»): весь остальной трафик → выбранный оффер (100%).
2. **Редактор офферов существующей кампании** (логика повторяет эталонное видео).
   - **Fetch Streams** подтягивает все потоки кампании в локальную «обёртку» (PostgreSQL). При первом открытии это происходит автоматически. Потоки без офферов показываются просто как поток.
   - **Добавить** оффер по ID, **удалить** (оффер сереет, доля 0%, есть кнопка «Вернуть») и **запинить вес** (ввести долю, по умолчанию текущая) — это черновик. Поток подсвечивается жёлтым («Не опубликован»), в Keitaro ничего не меняется.
   - **Доли:** запиненные офферы сохраняют свою долю, остаток до 100% делится поровну между незапиненными активными (34/33/33, 25/25/25/25; с пином 25: 25 + 38/37).
   - **Push** отправляет в Keitaro только активные офферы с долями. Нужен хотя бы один активный оффер и сумма ровно 100%, иначе 422. Если поток успели поменять прямо в Keitaro после последнего Fetch, Push откажет с 409: нужно нажать Cancel, затем Fetch Streams и повторить правки. **Cancel** откатывает черновик к последнему опубликованному состоянию: добавленные в черновике офферы удаляются из обёртки.
   - Если оффер удалили прямо в Keitaro, после Fetch Streams он становится removed с кнопкой «Вернуть».
   - Рядом с офферами показана статистика: клики, конверсии, CR, доход, EPC, прибыль за выбранный период.

Каждый Push записывается в журнал (PostgreSQL) со снимком «было / стало» из Keitaro. Созданные кампании тоже сохраняются в БД.

## Стек

| | |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2 (async, asyncpg), Alembic, httpx, pydantic-settings, uv |
| Frontend | React 19, Vite, TypeScript, React Router, TanStack Query, Tailwind CSS 4, shadcn/ui, Feature-Sliced Design, openapi-fetch |
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

Нужен только Docker с Compose v2 (`docker compose version`). Python и Node для этого варианта не нужны.

**1. Настройки.** Скопируйте шаблон и заполните его:

```bash
cp .env.example .env
```

| Переменная | Что вписать |
|---|---|
| `KEITARO_BASE_URL` | адрес трекера, например `https://tracker.example` (без `/admin`) |
| `KEITARO_API_KEY` | ключ Admin API из админки Keitaro (там же документация API: `https://<трекер>/admin/?object=adminApi`) |
| `KEITARO_DEFAULT_DOMAIN_ID`, `KEITARO_DEFAULT_GROUP_ID`, `KEITARO_DEFAULT_TRAFFIC_SOURCE_ID` | ID домена, группы кампаний и источника для новых кампаний. Можно не заполнять и выбирать их в форме; ID видны в админке Keitaro или по `GET /api/reference/domains`, `groups`, `traffic-sources` после запуска |
| `CAMPAIGN_NAME_PREFIX` | префикс имени кампаний, например `test_ivanov_` |
| `KEITARO_CACHE_TTL_SECONDS` | сколько секунд кэшировать списки кампаний и офферов (по умолчанию 60, `0` отключает) |
| `POSTGRES_*`, `DATABASE_URL` | можно оставить как в шаблоне |

**2. Запуск:**

```bash
make up            # то же самое без make: docker compose up --build -d
```

| Что | Адрес |
|---|---|
| UI | http://localhost:8080 (создание кампании), http://localhost:8080/campaigns/&lt;ID&gt; (редактор кампании) |
| API и Swagger | http://localhost:8000/docs |
| PostgreSQL | localhost:5433 (логин и пароль из `.env`) |

Миграции применяются автоматически при старте контейнера `backend` (`alembic upgrade head`). Если какой-то порт занят, поменяйте его слева в `ports:` в `docker-compose.yml`.

**3. Проверка, что всё работает:**

```bash
curl http://localhost:8000/api/health              # {"status":"ok"}
curl http://localhost:8000/api/reference/defaults  # ваши ID и префикс из .env
```

Затем в UI на вкладке «Создать кампанию» заполните название, гео и оффер. Ссылка на кампанию появится под формой, а «Открыть в редакторе» откроет её офферы.

**Логи и остановка:**

```bash
make logs          # docker compose logs -f backend
make down          # docker compose down (данные БД остаются в volume pgdata)
docker compose down -v   # остановить и удалить данные БД
```

Все настройки лежат в одном файле `.env` в корне репозитория. Его читают и docker compose, и бэкенд при локальном запуске.

## Локальная разработка

Нужны [uv](https://docs.astral.sh/uv/) (он сам поставит Python 3.13), Node 22+, Docker (для Postgres) и `make` (`sudo apt install make`; без него можно выполнять команды из `Makefile` вручную). `.env` нужен тот же, что и для Docker.

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
- `offer_changes`: журнал Push: офферы потока в Keitaro до и после;
- `streams`, `stream_offers`: обёртка потоков с черновиками, пинами и снимком последней публикации.

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
| GET | `/api/campaigns/{id}/editor?interval=` | потоки из обёртки, офферы, доли, пины и статистика (при первом открытии — Fetch) |
| POST | `/api/campaigns/{id}/streams/fetch` | Fetch Streams из Keitaro |
| POST | `/api/campaigns/{id}/streams/{sid}/offers` | черновик: добавить оффер `{offer_id}` |
| DELETE | `/api/campaigns/{id}/streams/{sid}/offers/{offer_id}` | черновик: удалить (removed, 0%) |
| POST | `/api/campaigns/{id}/streams/{sid}/offers/{offer_id}/restore` | черновик: вернуть |
| PUT / DELETE | `/api/campaigns/{id}/streams/{sid}/offers/{offer_id}/pin` | черновик: запинить `{share}` или открепить |
| POST | `/api/campaigns/{id}/streams/{sid}/push` | опубликовать в Keitaro |
| POST | `/api/campaigns/{id}/streams/{sid}/cancel` | отменить черновик |
| GET | `/api/campaigns/{id}/changes` | журнал публикаций (Push) |

## Допущения

- Логика редактора восстановлена по расшифровке эталонного видео и записана в `.grace/context/requirements.xml` → `Decisions`. Как задаётся значение пина, в видео не видно: сделан ввод с дефолтом «текущая доля». Статистика по офферам в видео не показана, но оставлена.
- API-ключ в тестовом трекере видит только часть офферов. Поэтому в редакторе оффер можно добавить и по ID вручную, а у офферов без доступа на чтение вместо названия показывается `Offer #ID`.

## Разработка с агентами (GRACE)

Правила для агентов лежат в [`AGENTS.md`](AGENTS.md) (`CLAUDE.md` — симлинк на него). Коротко:

- тесты не пишем;
- любое изменение контракта API и поведения проходит через `grace-spec` → `grace-plan` → `grace-execute`;
- мелкие правки UI можно делать напрямую.

CLI GRACE: `bun add -g @osovv/grace-cli`.
