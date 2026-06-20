# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Support Ticket Management API Service — a FastAPI backend for managing customer support tickets, built as a job assignment for Everestek Technosoft Solutions. Not everything in `docs/Backend Engineering Assignment.pdf` will be implemented; the user will direct what to build. Refer to `docs/ER Diagram.png` when designing new ORM models — it is the authoritative schema reference.

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
make run ENV=<env>
```
`make run` passes `.envs/{env}/api.env` to Docker Compose for variable substitution in the compose file (e.g. `${SERVER_PORT}`). The containers themselves load both `.envs/{env}/api.env` and `.envs/{env}/db.env` via the `env_file` key inside the compose YAML.

`server.sh` is the container entrypoint — runs uvicorn with `--reload` when `ENVIRONMENT=local`, without it otherwise.

## Docker Compose Services

Each compose file defines four services: `server`, `celery`, `postgres`, `redis`.

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
| `JWTSettings` | `JWT_` | `JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY` |

### Database

- Inject the async session via `get_session` from `src.core.database` as a FastAPI dependency.
- All ORM models extend `Base` from `src.core.models`. `Base` auto-includes an `id: Mapped[int]` integer primary key — do not redeclare it in subclasses.
- SQL echo is enabled automatically when `ENVIRONMENT=local`.
- `BaseRepository[ModelT]` in `src/core/repository.py` provides `get`, `list`, `add`, `delete`. Domain repos extend it and add query methods (e.g. `get_by_email`). Domain repo dependency factories live in `src/{app}/dependencies.py`.
- Repository methods use `session.flush()`, not `session.commit()`. `get_session` commits on success and rolls back on exception — never call `session.commit()` in a repo or service.
- When adding a new domain's ORM models, import the models module in `alembic/env.py`: `from src.{app} import models as _  # noqa: F401`. Without this, `--autogenerate` produces an empty migration.

### Celery

- The Celery app instance is at `src.core.celery:app`.
- All tasks use JSON serialization and UTC timezone (configured in `src/core/celery.py` — do not override per-task).
- Place tasks in `src/{app}/tasks.py` within the relevant domain app.

### Constants

- Shared constants (`PROJECT_NAME`, `API_V1_PREFIX`, `APP_STARTUP_MSG`, `APP_SHUTDOWN_MSG`, `DEFAULT_ERROR_MSG`, `Environment`) live in `src/core/constants.py`.
- Domain constants (endpoint paths, cookie names, token types, algorithm, error messages, enums, field limits) live in `src/{app}/constants.py`.
- Define constants for all meaningful string literals — endpoint paths, cookie names, token types, error messages, algorithm names, and log messages. A value used in only one place still warrants a constant if it represents a meaningful domain value. Log message strings are defined as constants (personal preference).

### Logging

- Always use `structlog.get_logger(__name__)`, never `logging.getLogger`.
- `src/core/logging/constants.py` must stay free of project imports — it is the only logging file that `src/core/config.py` can safely import from without causing a circular import.
- Do not add `filter_by_level` to the structlog processor chain — level filtering is handled by `LOGGING_CONFIG`.
- Sensitive key matching is substring-based: any key whose name *contains* a sensitive word (e.g. `user_token`, `x_api_key`) is redacted, not just exact matches.
- `StructlogContextMiddleware` auto-binds `request_id`, `method`, `path`, `client_host` to structlog's context for every HTTP request. Do not re-bind these in route handlers or services.

### Domain Apps

Each domain lives under `src/{app}/` and follows this file layout:

| File | Purpose |
|------|---------|
| `constants.py` | `TABLE_NAME` string, enums, field-length limits, endpoint paths, error messages |
| `models.py` | SQLAlchemy ORM models extending `Base` |
| `schemas.py` | Pydantic request/response models |
| `services.py` | Business logic — no FastAPI imports allowed |
| `dependencies.py` | FastAPI `Depends` wiring: input extraction, repo/service instantiation |
| `router.py` | HTTP concerns only: request/response, cookies, status codes |
| `exceptions.py` | Domain exceptions extending `AppException` |
| `tasks.py` | Celery tasks (only when async work is needed) |

`src/users/` and `src/auth/` are reference implementations.

### Layer Separation

Enforce strict separation between layers. Each layer has one responsibility and prohibited imports:

| Layer | File | Responsibility | Must not import |
|-------|------|---------------|-----------------|
| Router | `router.py` | HTTP only — cookies, status codes, request body, response | Business logic, DB |
| Dependencies | `dependencies.py` | Wire inputs and resources via `Depends` | Business logic |
| Services | `services.py` | All business logic, raise domain exceptions | `fastapi`, `Depends` |
| Repository | `repository.py` | Data access only | FastAPI, services |

Key placement rules:
- Business logic that raises a domain exception or makes a domain decision → **services**.
- Raw input extraction (`Cookie()`, `Header()`, `Query()`) → **router** parameter, not a dependency wrapper.
- Config-based wiring (e.g. `is_secure` checking `ENVIRONMENT`) → **dependencies**, not services.
- Repo instantiation → **dependencies** factory function (e.g. `get_user_repository`), injected into the router via `Depends`.

### Error Handling

- `AppException` base lives in `src/core/exceptions.py`. Subclasses set `status_code` and `detail` as **class attributes**, not constructor args.
- Domain exceptions live in `src/{app}/exceptions.py` and extend `AppException`.
- One generic handler in `src/core/exception_handlers.py` covers all `AppException` subclasses — no per-exception handlers.
- Register with `app.add_exception_handler(AppException, app_exception_handler)` in `main.py`.
- Always use `starlette.status` constants (e.g. `status.HTTP_401_UNAUTHORIZED`), never raw integers.
- Error message strings are constants in `src/{app}/constants.py`.

### Authentication

- **JWT algorithm**: RS256 (asymmetric). Private key signs; public key verifies. Both stored as env vars (`JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`).
- Tokens are delivered via httpOnly cookies **only** — never in the response body.
- Cookie settings applied to all auth cookies: `httponly=True`, `samesite=CookieSameSite.STRICT.value`, `secure=is_secure()`.
- `secure=True` when `ENVIRONMENT != local`; `False` on local to allow HTTP.
- Access token cookie path: `/` (sent with every request). Refresh token cookie path: `/api/v1/auth/refresh` (limits exposure to the refresh endpoint only).
- `CookieSameSite` is a `(str, Enum)` — consistent with `UserRole` and `Environment`.
- Use `LoginResponse.model_validate(orm_instance)` with `model_config = ConfigDict(from_attributes=True)` in response schemas instead of manually mapping ORM fields.
- `decode_token` stays as a standalone function, separate from `refresh_access_token` — it is a reusable cryptographic primitive that future token-authenticated endpoints (e.g. `GET /me`) will call directly.

### API

- When adding a new domain router, two files must be updated:
  1. `src/api/v1/router.py` — include the domain router following the auth pattern: import the prefix constant and the router, then call `router.include_router(...)`.
  2. `src/core/openapi.py` — import the tag constants from `src.{app}.constants` and append to `OPENAPI_TAGS`.
- `OPENAPI_TAGS` lives in `src/core/openapi.py` — **not** `src/core/constants.py`. Domain constants import from `src.core.constants`; the reverse would create a circular import.
- Tag name and description are constants in `src/{app}/constants.py` (e.g. `AUTH_TAG`, `AUTH_TAG_DESCRIPTION`).
- Swagger UI is at `/docs`, ReDoc at `/redoc`.
