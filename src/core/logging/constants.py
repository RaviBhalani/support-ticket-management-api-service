import re
from enum import Enum

# Middleware
HTTP_SCOPE_TYPE = "http"

# Redaction
REDACTION_TEXT = "***REDACTED***"
TOKEN_PATTERN = (
    r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"
    r"|Basic\s+[A-Za-z0-9+/]+=*"
    r"|\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"
)
SENSITIVE_KEYS = frozenset({
    "password",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "api_key",
    "secret",
    "jwt",
})
SENSITIVE_VALUE_RE = re.compile(TOKEN_PATTERN)

# Enums
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogRenderer(str, Enum):
    JSON = "json"
    CONSOLE = "console"
