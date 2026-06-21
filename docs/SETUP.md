# Support Ticket Management API Service

REST API for managing customer support tickets, built with FastAPI. Submitted as a job assignment for Everestek Technosoft Solutions.

## Overview

The service provides ticket lifecycle management for two user roles — **Customers** and **Agents**. Customers submit and delete their own tickets; agents manage ticket status and assignment. Authentication is handled via short-lived access tokens and longer-lived refresh tokens, both delivered as httpOnly cookies.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.14 |
| Web Framework | FastAPI 0.137 |
| Database | PostgreSQL 18 (async via psycopg3 + SQLAlchemy 2.0) |
| Cache / Message Broker | Redis 8 |
| Task Queue | Celery 5 |
| Containerization | Docker & Docker Compose |

## Prerequisites

- Docker and Docker Compose
- Python 3.14 (for running scripts outside Docker)
- Git Bash or a POSIX-compatible shell (to run `setup.sh`)

---

## Quick Setup (Reviewer)

The required `.envs/local/` env files will be provided separately via email. Once received, place them at:

```
.envs/local/api.env
.envs/local/db.env
```

Then run the one-command setup script:

```bash
./setup.sh
```

This single script tears down any existing containers, rebuilds images, starts all four services, waits for PostgreSQL to be ready, applies all migrations, creates a local virtual environment, installs Python dependencies, and seeds the database with sample agents and customers.

> **Once complete, the script prints a sample of 5 agents and 20 customers to the terminal — not the full set of 100 agents and 10 000 customers. Use any of those credentials to log in and test the API. The password for every seeded user follows the format `firstname_lastname` in lowercase (e.g. a user named John Smith has password `john_smith`).**

---

## Normal Local Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd support-ticket-management-api-service
```

### 2. Create environment files

The committed templates are at `.envs/api.env` and `.envs/db.env`. Copy them into the local environment folder and fill in the required values:

```bash
mkdir -p .envs/local
cp .envs/api.env .envs/local/api.env
cp .envs/db.env .envs/local/db.env
```

See the [Environment Variables](#environment-variables) section for what each variable means and which ones are required.

### 3. Generate an RSA key pair for JWT signing

```bash
openssl genrsa -out private.pem 1024
openssl rsa -in private.pem -pubout -out public.pem
```

Paste the full PEM contents of each file into `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY` in `.envs/local/api.env` (keep them on a single line or use multiline quoting as shown in the template).

### 4. Start services

```bash
docker compose -f docker-compose.local.yaml --env-file .envs/local.env up -d --build
```

### 5. Apply database migrations

```bash
docker compose -f docker-compose.local.yaml --env-file .envs/local.env exec server alembic upgrade head
```

### 6. Seed the database

```bash
python -m venv .venv

# Windows (Git Bash / PowerShell)
.venv/Scripts/pip install -r requirements/local.txt

# macOS / Linux
.venv/bin/pip install -r requirements/local.txt

cd scripts && python seed.py && python sample_users.py && cd ..
```

---

## Environment Variables

### `.envs/local/api.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_ENVIRONMENT` | _(required)_ | Runtime environment: `local`, `dev`, `test`, or `prod` |
| `SERVER_HOST` | `0.0.0.0` | Host the server binds to |
| `SERVER_PORT` | `8000` | Port the server listens on |
| `CORS_ALLOWED_ORIGINS` | `[]` | JSON array of allowed CORS origins |
| `CORS_ALLOWED_METHODS` | `["GET","POST",...]` | Allowed HTTP methods |
| `CORS_ALLOWED_HEADERS` | `["*"]` | Allowed request headers |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials in CORS requests |
| `JWT_PRIVATE_KEY` | _(required)_ | RSA private key (PEM) for signing tokens |
| `JWT_PUBLIC_KEY` | _(required)_ | RSA public key (PEM) for verifying tokens |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token TTL in minutes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL in days |
| `LOG_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_RENDERER` | `console` | Output format: `console` or `json` |
| `LOG_TIMEZONE` | `UTC` | Timezone for log timestamps |
| `LOG_ENABLE_COLORED_CONSOLE_LOGS` | `false` | ANSI colours in console output |
| `LOG_ENABLE_RICH_TRACEBACK_FORMATTER` | `false` | Rich-formatted tracebacks |

### `.envs/local/db.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | _(required)_ | PostgreSQL username |
| `POSTGRES_PASSWORD` | _(required)_ | PostgreSQL password |
| `POSTGRES_DB` | _(required)_ | PostgreSQL database name |
| `POSTGRES_HOST` | `postgres` | PostgreSQL host (Docker service name) |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `REDIS_HOST` | `redis` | Redis host (Docker service name) |
| `REDIS_PORT` | `6379` | Redis port |

---

## Running Locally

### With Docker (recommended)

```bash
# Start all services (server, celery, postgres, redis)
docker compose -f docker-compose.local.yaml --env-file .envs/local.env up -d

# Stop services
docker compose -f docker-compose.local.yaml --env-file .envs/local.env down

# Stop and wipe all volumes
docker compose -f docker-compose.local.yaml --env-file .envs/local.env down --volumes
```

### Without Docker (requires external Postgres and Redis)

```bash
# FastAPI server with hot reload
uvicorn src.main:app --reload

# Celery worker
celery -A src.core.celery worker --loglevel=info
```

### Database migrations

```bash
# Apply all pending migrations
docker compose -f docker-compose.local.yaml --env-file .envs/local.env exec server alembic upgrade head

# Roll back one migration
docker compose -f docker-compose.local.yaml --env-file .envs/local.env exec server alembic downgrade -1
```

---

## API Documentation

With the server running, interactive docs are available at:

| Interface | URL |
|-----------|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |

All endpoints are versioned under `/api/v1`. Authenticated endpoints require a valid `access_token` httpOnly cookie obtained from `POST /api/v1/auth/login`.
