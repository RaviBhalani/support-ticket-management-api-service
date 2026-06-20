from enum import Enum

PROJECT_NAME = "support_ticket_management"
PROJECT_DESCRIPTION = "REST API for managing customer support tickets."
PROJECT_VERSION = "1.0.0"
API_V1_PREFIX = "/api/v1"
DOCS_URL = "/docs"
REDOC_URL = "/redoc"
OPENAPI_URL = "/openapi.json"


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


# Settings env_prefix
SERVER_ENV_PREFIX = "SERVER_"
POSTGRES_ENV_PREFIX = "POSTGRES_"
REDIS_ENV_PREFIX = "REDIS_"
LOG_ENV_PREFIX = "LOG_"
CORS_ENV_PREFIX = "CORS_"
JWT_ENV_PREFIX = "JWT_"

# Server defaults
SERVER_DEFAULT_HOST = "0.0.0.0"
SERVER_DEFAULT_PORT = 8000

# Database defaults and URL components
DB_DEFAULT_HOST = "postgres"
DB_DEFAULT_PORT = 5432
DB_DRIVER = "postgresql"
DB_ASYNC_DRIVER = "asyncpg"

# Redis defaults
REDIS_DEFAULT_HOST = "redis"
REDIS_DEFAULT_PORT = 6379
REDIS_DEFAULT_DB = 0
REDIS_SCHEME = "redis"

# HTTP methods
HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_PATCH = "PATCH"
HTTP_METHOD_DELETE = "DELETE"
HTTP_METHOD_OPTIONS = "OPTIONS"

# JWT defaults
JWT_DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7

SERIALIZER_JSON = "json"
TIMEZONE_UTC = "UTC"

DEFAULT_ERROR_MSG = "An unexpected error occurred."

APP_STARTUP_MSG = "Starting up"
APP_SHUTDOWN_MSG = "Shutting down"
