import logging.config
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from src.core.constants import PROJECT_NAME, PROJECT_DESCRIPTION, PROJECT_VERSION, DOCS_URL, REDOC_URL, OPENAPI_URL
from src.core.database import dispose_engine
from src.core.logging.config import LOGGING_CONFIG, configure_structlog

configure_structlog()
logging.config.dictConfig(LOGGING_CONFIG)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up")
    yield
    await dispose_engine()
    logger.info("Shutting down")


app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=PROJECT_VERSION,
    lifespan=lifespan,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)
