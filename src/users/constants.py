from enum import Enum

TABLE_NAME = "users"

class UserRole(str, Enum):
    AGENT = "agent"
    CUSTOMER = "customer"

NAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 255
PASSWORD_MAX_LENGTH = 255
ROLE_MAX_LENGTH = max(len(role.value) for role in UserRole)
