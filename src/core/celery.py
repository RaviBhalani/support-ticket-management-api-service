from celery import Celery

from src.core.config import settings
from src.core.constants import PROJECT_NAME, SERIALIZER_JSON, TIMEZONE_UTC

app = Celery(
    PROJECT_NAME,
    broker=settings.redis.url,
    backend=settings.redis.url,
)

app.conf.update(
    task_serializer=SERIALIZER_JSON,
    accept_content=[SERIALIZER_JSON],
    result_serializer=SERIALIZER_JSON,
    timezone=TIMEZONE_UTC,
    enable_utc=True,
)
