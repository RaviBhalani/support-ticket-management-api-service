from enum import Enum

PROJECT_NAME = "support_ticket_management"


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"
