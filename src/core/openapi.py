from src.auth.constants import AUTH_TAG, AUTH_TAG_DESCRIPTION

OPENAPI_TAGS: list[dict[str, str]] = [
    {"name": AUTH_TAG, "description": AUTH_TAG_DESCRIPTION},
]
