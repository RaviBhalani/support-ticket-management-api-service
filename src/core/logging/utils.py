import json
from datetime import datetime
from zoneinfo import ZoneInfo

from src.core.config import settings
from src.core.logging.constants import (
    REDACTION_TEXT,
    SENSITIVE_KEYS,
    SENSITIVE_VALUE_RE,
)

LOG_TZ_INFO = ZoneInfo(settings.logging.timezone)


def _redact_value(value):
    if isinstance(value, str):
        return REDACTION_TEXT if SENSITIVE_VALUE_RE.search(value) else value

    if isinstance(value, bytes):
        try:
            decoded = value.decode("utf-8")
            if decoded.startswith("{") or decoded.startswith("["):
                data = json.loads(decoded)
                return json.dumps(_redact_value(data))
            return REDACTION_TEXT if SENSITIVE_VALUE_RE.search(decoded) else value
        except Exception:
            return value

    if isinstance(value, dict):
        return {k: _redact_entry(k, v) for k, v in value.items()}

    if isinstance(value, list):
        return [_redact_value(v) for v in value]

    return value


def _redact_entry(key, value):
    if isinstance(key, str) and any(s in key.lower() for s in SENSITIVE_KEYS):
        return REDACTION_TEXT
    return _redact_value(value)


def redact_sensitive_data(logger, method_name, event_dict):
    for key in event_dict:
        event_dict[key] = _redact_entry(key, event_dict[key])
    return event_dict


def log_timestamper(logger, method_name, event_dict):
    event_dict["timestamp"] = datetime.now(LOG_TZ_INFO).isoformat()
    return event_dict
