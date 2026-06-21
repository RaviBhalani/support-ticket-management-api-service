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
| Seed database with agents + customers | `make seed` |

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
- `BaseRepository[ModelT]` in `src/core/repository.py` provides `get`, `list`, `add`, `delete`, `flush`, `refresh`. Domain repos extend it and add query methods (e.g. `get_by_email`). Domain repo dependency factories live in `src/{app}/dependencies.py`. Call `repo.flush()` then `repo.refresh(instance)` after mutating an ORM object when you need server-generated values (e.g. `modified_ts` from `onupdate=func.now()`) to be present on the instance before Pydantic serialises it — asyncpg does not return UPDATE results via RETURNING, so SQLAlchemy marks the object expired after a flush.
- Repository methods use `session.flush()`, not `session.commit()`. `get_session` commits on success and rolls back on exception — never call `session.commit()` in a repo or service.
- When adding a new domain's ORM models, import the models module in `alembic/env.py`: `from src.{app} import models as _  # noqa: F401`. Without this, `--autogenerate` produces an empty migration.
- FK references use constants: define `<ENTITY>_FK = f"{TABLE_NAME}.id"` in `src/{app}/constants.py` (e.g., `USER_FK = f"{TABLE_NAME}.id"` in `src/users/constants.py`). Import this constant in any model that references the entity as a foreign key — never hardcode `"users.id"` inside a model file.
- `ON_DELETE_SET_NULL` and `ON_DELETE_CASCADE` are string constants in `src/core/constants.py`. Always import and pass them to `ForeignKey(..., ondelete=ON_DELETE_CASCADE)` — never hardcode the string.
- Two reusable timestamp mixins live in `src/core/mixins.py` (both declare `__abstract__ = True`):
  - `CreatedAtMixin`: adds `created_ts: Mapped[datetime]` with `server_default=func.now()`.
  - `TimestampMixin(CreatedAtMixin)`: inherits `created_ts` and adds `modified_ts: Mapped[datetime]` with `server_default=func.now(), onupdate=func.now()`.
  - Use `TimestampMixin` for entities that track both creation and last-modified time. Use `CreatedAtMixin` for append-only records (e.g., history entries).
- `sync_session_factory` in `src.core.database`: a synchronous `sessionmaker` for use inside Celery tasks (which run synchronously). Use with `with sync_session_factory() as session:`. Never use `async_session_factory` in a Celery task.

### Celery

- The Celery app instance is at `src.core.celery:app`.
- All tasks use JSON serialization and UTC timezone (configured in `src/core/celery.py` — do not override per-task).
- Place tasks in `src/{app}/tasks.py` within the relevant domain app.
- Celery tasks that need DB access must use `sync_session_factory` from `src.core.database` — Celery workers run synchronously, not in an async event loop.
- Email templates: place HTML files in `src/{app}/templates/`. Load with `read_template(__file__, template_name)` from `src.core.utils`. Use `str.replace("{{placeholder}}", value)` chains for substitution. Use `DATETIME_DISPLAY_FORMAT` from `src.core.constants` to format `datetime` values for display.

### Pagination & Filtering

For paginated list endpoints use `fastapi-pagination` + `fastapi-filter` (both in `requirements/base.txt`).

- **Service layer:** the `list_*` service function is **synchronous** and returns a SQLAlchemy `Select` statement — not a list. It delegates to the repo's query-builder method.
- **Repository layer:** the query-builder (e.g. `list_query_for_user`) applies `WHERE`/`ORDER BY` and returns a `Select`. Do not execute the query here.
- **Router layer:** call `paginate(deps.session, query, params=params, transformer=...)` from `fastapi_pagination.ext.sqlalchemy`. The `transformer` lambda selects the correct response schema per role: `lambda items: [Schema.model_validate(t) for t in items]`.
- **Filter class:** subclass `fastapi_filter.contrib.sqlalchemy.Filter`. Declare fields with the `__in` suffix for multi-value filtering and set `Constants.model = YourModel`. Inject with `FilterDepends(YourFilter)` in the router.
- **Pagination params:** inject `params: Params = Depends()` from `fastapi_pagination`. Default `size` is 50; no custom pagination constants are needed.
- **`add_pagination(app)`** is not required when calling `paginate()` explicitly in route handlers — avoid it to keep `main.py` minimal.

### Dependency Bundling

When a router needs multiple repositories **and** a session (required by `paginate()`), group them into a `NameDependencies` class instead of listing four `Depends(...)` parameters on every endpoint:

```python
class TicketDependencies:
    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        repo: TicketRepository = Depends(get_ticket_repository),
        history_repo: TicketHistoryRepository = Depends(get_ticket_history_repository),
        user_repo: UserRepository = Depends(get_user_repository),
    ) -> None:
        self.session = session
        self.repo = repo
        self.history_repo = history_repo
        self.user_repo = user_repo
```

Endpoints declare `deps: TicketDependencies = Depends()`. The `session` attribute is required because `paginate()` takes it directly. Standalone factory functions (`get_ticket_repository`, etc.) still exist for injection outside the bundle.

### Scripts

- Standalone scripts live in `scripts/` at the project root, parallel to `alembic/` and `src/`.
- `scripts/utils.py` provides shared bootstrap for all scripts:
  - `setup_path()` — inserts the project root into `sys.path` so `src.*` imports resolve.
  - `load_envs()` — loads `.envs/local/api.env` and `.envs/local/db.env` into `os.environ`.
  - `run_async(coro)` — wraps `asyncio.run()` with an explicit `SelectorEventLoop`. Required on Windows because the default `ProactorEventLoop` is incompatible with psycopg async.
- Every script must call `utils.setup_path()` and `utils.load_envs()` **before** any `src.*` import.
- Scripts call `await session.commit()` directly — they are not bound by the repo flush-only contract.

### Constants

- Shared constants (`PROJECT_NAME`, `API_V1_PREFIX`, `APP_STARTUP_MSG`, `APP_SHUTDOWN_MSG`, `DEFAULT_ERROR_MSG`, `Environment`) live in `src/core/constants.py`.
- Domain constants (endpoint paths, cookie names, token types, algorithm, error messages, enums, field limits) live in `src/{app}/constants.py`.
- Define constants for all meaningful string literals — endpoint paths, cookie names, token types, error messages, algorithm names, and log messages. A value used in only one place still warrants a constant if it represents a meaningful domain value. Log message strings are defined as constants (personal preference).
- `PASSWORD_MAX_LENGTH = 60` — bcrypt hashes are always exactly 60 characters regardless of input length.

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

When a detail endpoint must return related entity data (not raw FK ids), define a compact summary schema (e.g., `TicketUserResponse` with `id`, `first_name`, `last_name`, `email`) and override the FK field in the detail response schema with the summary type (`customer: TicketUserResponse | None`). The service fetches the related objects and returns them alongside the main entity (as extra tuple elements). The router constructs the response with `model_dump(exclude={"related_field_name"})` to drop the raw integer FK before merging in the validated summary objects via `**detail_fields`.

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
- Use 409 Conflict (`status.HTTP_409_CONFLICT`) for operations blocked by the current resource state — e.g., attempting to modify a ticket that is already RESOLVED or CLOSED. 409 means "the request is valid but conflicts with the current state of the resource"; it is distinct from 422 (validation failure) and 403 (authorization denied).

### Authentication

- **JWT algorithm**: RS256 (asymmetric). Private key signs; public key verifies. Both stored as env vars (`JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`). `PyJWT` requires the `cryptography` package for RS256 — pin it explicitly as a direct dependency.
- **Password hashing**: use `bcrypt` directly (`bcrypt.checkpw`, `bcrypt.hashpw`) — not `passlib`, which is abandoned (last release 2020) and breaks with `bcrypt >= 4.0`.
- Tokens are delivered via httpOnly cookies **only** — never in the response body.
- Cookie settings applied to all auth cookies: `httponly=True`, `samesite=CookieSameSite.STRICT.value`, `secure=is_secure()`.
- `secure=True` when `ENVIRONMENT != local`; `False` on local to allow HTTP.
- Access token cookie path: `/` (sent with every request). Refresh token cookie path: `/api/v1/auth/refresh` (limits exposure to the refresh endpoint only).
- `CookieSameSite` is a `(str, Enum)` — consistent with `UserRole` and `Environment`.
- Use `LoginResponse.model_validate(orm_instance)` with `model_config = ConfigDict(from_attributes=True)` in response schemas instead of manually mapping ORM fields.
- `decode_token` stays as a standalone function, separate from `refresh_access_token` — it is a reusable cryptographic primitive that future token-authenticated endpoints (e.g. `GET /me`) will call directly.
- Auth dependencies in `src/auth/dependencies.py`:
  - `get_current_user` — reads the `access_token` cookie, calls `decode_token`, validates token type is `"access"`, fetches the user by id. Raises `InvalidTokenTypeError` or `InvalidCredentialsError` as appropriate.
  - `require_authentication` — pure pass-through alias for `get_current_user`; makes intent explicit in router signatures for any-role endpoints.
  - `require_agent` / `require_customer` — check `current_user.role` and raise `AgentRequiredError` (403) or `CustomerRequiredError` (403). Message constants `AGENT_REQUIRED_MSG` / `CUSTOMER_REQUIRED_MSG` live in `src/auth/constants.py`; the exceptions live in `src/auth/exceptions.py`.

### API

- When adding a new domain router, two files must be updated:
  1. `src/api/v1/router.py` — include the domain router following the auth pattern: import the prefix constant and the router, then call `router.include_router(...)`.
  2. `src/core/openapi.py` — import the tag constants from `src.{app}.constants` and append to `OPENAPI_TAGS`.
- `OPENAPI_TAGS` lives in `src/core/openapi.py` — **not** `src/core/constants.py`. Domain constants import from `src.core.constants`; the reverse would create a circular import.
- Tag name and description are constants in `src/{app}/constants.py` (e.g. `AUTH_TAG`, `AUTH_TAG_DESCRIPTION`).
- Swagger UI is at `/docs`, ReDoc at `/redoc`.
