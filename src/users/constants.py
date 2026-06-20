from enum import Enum

# Table
TABLE_NAME = "users"

# Roles
class UserRole(str, Enum):
    AGENT = "agent"
    CUSTOMER = "customer"

# Field limits
NAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 255
PASSWORD_MAX_LENGTH = 60
ROLE_MAX_LENGTH = max(len(role.value) for role in UserRole)
