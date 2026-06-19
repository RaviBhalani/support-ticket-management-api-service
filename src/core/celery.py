from celery import Celery

from src.core.config import settings
from src.core.constants import PROJECT_NAME

app = Celery(
    PROJECT_NAME,
    broker=settings.redis.url,
    backend=settings.redis.url,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
