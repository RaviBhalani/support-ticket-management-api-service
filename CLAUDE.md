# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Support Ticket Management API Service — a FastAPI backend for managing customer support tickets, built as a job assignment for Everestek Technosoft Solutions. Not everything in `docs/Backend Engineering Assignment.pdf` will be implemented; the user will direct what to build.

## Tech Stack

- **Language**: Python 3.14
- **Web framework**: FastAPI
- **Database**: PostgreSQL (async via asyncpg + SQLAlchemy 2.0)
- **Cache / broker**: Redis
- **Task queue**: Celery 5.x (broker and backend both Redis)
- **Containerization**: Docker & Docker Compose

## Environment Setup

Four environments: `local`, `dev`, `test`, `prod`.

**Env files**: `.envs/api.env` and `.envs/db.env` are committed templates. Copy them into `.envs/{env}/api.env` and `.envs/{env}/db.env` and fill in values. The `.envs/{env}/` folders are gitignored.

**Requirements**: `requirements/base.txt` holds shared deps; each env file extends it with `-r base.txt`. Install with:
```bash
pip install -r requirements/{env}.txt
```

**Run with Docker**:
```bash
make run ENV=<env>   # tears down and rebuilds using docker-compose.{env}.yaml + .envs/{env}/api.env
```

`server.sh` is the container entrypoint — runs uvicorn with `--reload` when `ENVIRONMENT=local`, without it otherwise.

## Docker Compose Services

Each compose file defines four services: `server`, `celery`, `db` (PostgreSQL), `redis`.

## Common Commands

| Task | Command |
|------|---------|
| Rebuild & start Docker services | `make run ENV=<env>` |
| Generate a migration (inside Docker) | `make migration ENV=<env> msg="<message>"` |
| Apply pending migrations (inside Docker) | `make upgrade` |
| Roll back last migration (inside Docker) | `make downgrade` |
| Run dev server (outside Docker) | `uvicorn src.main:app --reload` |
| Run Celery worker (outside Docker) | `celery -A src.core.celery worker --loglevel=info` |

No test suite exists yet. Commands will be added once `tests/` is established.

## Conventions

### Dependencies

Always pin package versions explicitly in requirements files (e.g. `fastapi==0.115.12`). Never add a transitive dependency as an explicit entry.

### Configuration

Access all settings via the singleton: `from src.core.config import settings`. The settings classes and their env-var prefixes are:

| Class | Prefix | Example var |
|-------|--------|-------------|
| `ServerSettings` | _(none)_ | `ENVIRONMENT`, `SERVER_PORT` |
| `DatabaseSettings` | `POSTGRES_` | `POSTGRES_USER`, `POSTGRES_DB` |
| `RedisSettings` | `REDIS_` | `REDIS_HOST`, `REDIS_PORT` |
| `LoggingSettings` | _(none)_ | `LOG_LEVEL`, `LOG_RENDERER` |
| `CORSSettings` | `CORS_` | `CORS_ALLOWED_ORIGINS`, `CORS_ALLOW_CREDENTIALS` |

### Database

- Inject the async session via `get_session` from `src.core.database` as a FastAPI dependency.
- All ORM models extend `Base` from `src.core.models`. `Base` auto-includes an `id: Mapped[int]` integer primary key — do not redeclare it in subclasses.
- SQL echo is enabled automatically when `ENVIRONMENT=local`.

### Celery

- The Celery app instance is at `src.core.celery:app`.
- All tasks use JSON serialization and UTC timezone (configured in `src/core/celery.py` — do not override per-task).
- Place tasks in `src/{app}/tasks.py` within the relevant domain app.

### Constants

- App-level metadata (`PROJECT_NAME`, `PROJECT_DESCRIPTION`, `PROJECT_VERSION`, `DOCS_URL`, `REDOC_URL`, `OPENAPI_URL`) lives in `src/core/constants.py`.
- Do not define constants for log message strings — log inline. A constant is only justified when a value is reused across multiple call sites or is non-obvious from the literal.

### Logging

- Always use `structlog.get_logger(__name__)`, never `logging.getLogger`.
- `src/core/logging/constants.py` must stay free of project imports — it is the only logging file that `src/core/config.py` can safely import from without causing a circular import.
- Do not add `filter_by_level` to the structlog processor chain — level filtering is handled by `LOGGING_CONFIG`.
- Sensitive key matching is substring-based: any key whose name *contains* a sensitive word (e.g. `user_token`, `x_api_key`) is redacted, not just exact matches.

### Domain Apps

Each domain lives under `src/{app}/` and follows this file layout:

| File | Purpose |
|------|---------|
| `constants.py` | `TABLE_NAME` string, enums (e.g. `UserRole`), field-length limits |
| `models.py` | SQLAlchemy ORM models extending `Base` |
| `tasks.py` | Celery tasks (only when async work is needed) |

`src/users/` is the reference implementation. Add `router.py`, `schemas.py`, `services.py`, etc. as needed when building out endpoints.

### API

- When adding a router, pass `tags` to it and add a matching entry to `openapi_tags` in `main.py` so the Swagger UI shows grouped, described sections.
- Swagger UI is at `/docs`, ReDoc at `/redoc`.
