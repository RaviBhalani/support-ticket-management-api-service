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


DEFAULT_ERROR_MSG = "An unexpected error occurred."

APP_STARTUP_MSG = "Starting up"
APP_SHUTDOWN_MSG = "Shutting down"
