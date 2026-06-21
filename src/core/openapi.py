from src.auth.constants import AUTH_TAG, AUTH_TAG_DESCRIPTION
from src.tickets.constants import TICKETS_TAG, TICKETS_TAG_DESCRIPTION

OPENAPI_TAGS: list[dict[str, str]] = [
    {"name": AUTH_TAG, "description": AUTH_TAG_DESCRIPTION},
    {"name": TICKETS_TAG, "description": TICKETS_TAG_DESCRIPTION},
]
