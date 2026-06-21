# Architecture Decisions, Tradeoffs & Assumptions

## Architecture Decisions

### 1. Strict four-layer separation

Every domain follows the same layering: `router.py` → `dependencies.py` → `services.py` → `repository.py`. Each layer has a single responsibility and explicit rules about what it may not import. For example, services never import FastAPI; routers never contain business logic.

This makes each file's role immediately predictable: if there is a domain decision being made, it is in `services.py`; if a cookie is being set, it is in `router.py`.

### 2. Repository pattern with a generic base

`BaseRepository[ModelT]` provides `get`, `list`, `add`, `delete`, `flush`, and `refresh`. Domain repositories extend it and add query-builder methods. The base class keeps boilerplate out of domain code while leaving query logic close to the domain that owns it.

### 3. Session lifecycle: flush in repos, commit in the middleware

Repository methods call `session.flush()`, never `session.commit()`. The `get_session` dependency commits on success and rolls back on any exception. This means every request runs in exactly one transaction without individual handlers needing to manage it, and no handler can accidentally commit a partial state.

### 4. `flush()` + `refresh()` after UPDATE

SQLAlchemy marks ORM objects expired after a flush when asyncpg is the driver (asyncpg does not return UPDATE results via a `RETURNING` clause, so the values are unknown). Calling `repo.flush()` followed by `repo.refresh(instance)` re-issues a `SELECT` for the updated row, making server-generated values like `modified_ts` available before Pydantic serialises the response.

### 5. Dependency bundling via a `NameDependencies` class

When a router needs more than one repository plus a session (required by `fastapi_pagination`'s `paginate()` call), all four are grouped into a single `TicketDependencies` class injected with one `Depends()`. This avoids repeating four Depends parameters on every endpoint handler while keeping the individual factory functions available for injection elsewhere.

### 6. Service layer returns `Select` statements for list endpoints

The `list_tickets` service function returns a SQLAlchemy `Select` object, not a list. The router hands it directly to `paginate()`, which adds `LIMIT`/`OFFSET` and executes a single query. Returning a `Select` avoids fetching all rows into memory before slicing, and means the pagination library controls the actual execution.

### 7. Celery for async work with a synchronous session factory

Celery workers run synchronously (they are not inside an async event loop). A separate `sync_session_factory` is provided for tasks that need database access. This factory uses a synchronous psycopg driver alongside the async one used by FastAPI, so both paths share the same SQLAlchemy models and connection pool configuration without sharing an event loop.

### 8. RS256 JWT via httpOnly cookies only

Tokens are signed with an RSA private key and verified with the corresponding public key (asymmetric, RS256). Tokens are set exclusively as httpOnly, SameSite=Strict cookies — never returned in the response body. The access token is scoped to path `/`, the refresh token to `/api/v1/auth/refresh` to limit its exposure to exactly the one endpoint that needs it.

### 9. `bcrypt` directly, not `passlib`

`passlib` has not had a release since 2020 and breaks with `bcrypt >= 4.0`. `bcrypt.hashpw` / `bcrypt.checkpw` are called directly.

### 10. Structured logging via `structlog`

All loggers are obtained with `structlog.get_logger(__name__)`. A `StructlogContextMiddleware` auto-binds `request_id`, `method`, `path`, and `client_host` to structlog's context at the start of every request, so every log line emitted during that request carries the full context without needing to pass a logger around. Sensitive fields are redacted using substring matching on key names.

### 11. Priority derived from category, never set independently

Ticket priority is always computed from a `CATEGORY_PRIORITY_MAP` lookup on the ticket's category. There is no endpoint parameter to set priority directly. This is a deliberate domain rule: priority represents urgency, and urgency is a property of the ticket type, not a free-form field that users choose.

---

## Tradeoffs

### Async FastAPI + synchronous Celery

Running two database drivers (psycopg async for FastAPI, psycopg sync for Celery) adds a small dependency surface. The alternative — using `asyncio.run()` inside Celery tasks — would require careful event loop management and is unsupported on Windows. The two-driver approach keeps worker code straightforward and avoids async/sync boundary issues.

### Cookie-only authentication

Storing tokens in httpOnly cookies rather than returning them in the response body eliminates the most common token-theft vector (XSS accessing `localStorage`). The tradeoff is that API clients that cannot handle cookies (some CLI tools, certain third-party API clients) require extra configuration. For a support ticket system where the primary client is a browser, this is an acceptable constraint.

### No test suite yet

A test suite has not been established. The architecture — strict layer separation, a generic repository, domain exceptions as class attributes — is designed to make unit testing each layer in isolation straightforward without much framework setup. Adding `pytest-asyncio` with a test database and `httpx.AsyncClient` for integration tests would be the first step.

### `paginate()` requires an `AsyncSession` parameter

`fastapi_pagination`'s SQLAlchemy extension takes a session directly, which is why each router that paginates keeps a `session` attribute on its `Dependencies` class. This is slightly more coupling than ideal but avoids monkey-patching or overriding the library internals.

### Status transitions are final once RESOLVED or CLOSED

RESOLVED and CLOSED are terminal states. There is no admin override path to reopen a resolved ticket in the current implementation. This is an intentional simplification; a real system would likely need a reopen flow or a separate archival state.

---

## Assumptions

### Agent auto-assignment

When a ticket is created, the system automatically assigns it to the agent with the fewest currently open tickets (`get_agent_with_fewest_tickets()`). There is no manual assignment endpoint — agents cannot reassign tickets or pick them up themselves. If no agents exist, the `agent` field is left `NULL`.

### Scope of ticket visibility

- A **customer** can only see and delete their own tickets.
- An **agent** can only see and update tickets assigned to them.
- There is no global admin role or cross-agent visibility in the current implementation.

### Category drives priority

Priority is always a function of category. Updating a ticket's category automatically recalculates and overwrites the priority. There is no way to set priority independently — the schema does not expose it as a writable field.

### Ticket deletion is restricted to OPEN status

A customer may only delete a ticket while it is still OPEN. Once an agent has started work (`IN_PROGRESS`) or the ticket reaches a terminal state (`RESOLVED`, `CLOSED`), deletion is blocked with a 409 Conflict response. This prevents customers from deleting tickets that are mid-resolution.

### Email notification on creation only

A Celery task fires an email to the customer when a ticket is created. No other lifecycle events (status changes, assignment changes) trigger email notifications in the current implementation.

### One active environment per deployment

The four environment profiles (`local`, `dev`, `test`, `prod`) are meant for separate deployments. There is no multi-tenancy or runtime environment switching.

### Soft-delete is not used

Deleting a ticket (`DELETE /tickets/{id}`) performs a hard delete. Cascading `ON DELETE CASCADE` removes associated `ticket_history` rows. `ON DELETE SET NULL` nullifies the `customer` and `agent` FK columns on remaining tickets if a user is deleted.
