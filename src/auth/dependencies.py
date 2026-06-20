from src.core.config import settings
from src.core.constants import Environment


def is_secure() -> bool:
    return settings.server.environment != Environment.LOCAL
