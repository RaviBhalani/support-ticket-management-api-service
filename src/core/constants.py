from enum import Enum

PROJECT_NAME = "support_ticket_management"
PROJECT_DESCRIPTION = "REST API for managing customer support tickets."
PROJECT_VERSION = "1.0.0"
DOCS_URL = "/docs"
REDOC_URL = "/redoc"


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"
