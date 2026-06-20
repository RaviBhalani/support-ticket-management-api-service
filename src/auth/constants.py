from enum import Enum

from src.core.constants import API_V1_PREFIX

ROUTER_PREFIX = "/auth"
LOGIN_ENDPOINT = "/login"
REFRESH_ENDPOINT = "/refresh"

AUTH_TAG = "Auth"
AUTH_TAG_DESCRIPTION = "Authentication — login and token refresh."

ALGORITHM = "RS256"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"

ACCESS_COOKIE_PATH = "/"
REFRESH_COOKIE_PATH = f"{API_V1_PREFIX}{ROUTER_PREFIX}{REFRESH_ENDPOINT}"

class CookieSameSite(str, Enum):
    LAX = "lax"
    STRICT = "strict"
    NONE = "none"


INVALID_CREDENTIALS_MSG = "Invalid credentials"
TOKEN_EXPIRED_MSG = "Token has expired"
INVALID_TOKEN_MSG = "Invalid token"
REFRESH_TOKEN_MISSING_MSG = "Refresh token missing"
INVALID_TOKEN_TYPE_MSG = "Invalid token type"
