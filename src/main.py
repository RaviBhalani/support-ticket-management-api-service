import logging.config
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import router as api_v1_router
from src.core.config import settings
from src.core.exception_handlers import app_exception_handler
from src.core.exceptions import AppException
from src.core.constants import (
    API_V1_PREFIX,
    DOCS_URL,
    OPENAPI_URL,
    PROJECT_DESCRIPTION,
    PROJECT_NAME,
    PROJECT_VERSION,
    REDOC_URL
)
from src.core.database import dispose_engine
from src.core.logging.config import LOGGING_CONFIG, configure_structlog
from src.core.logging.middlewares import StructlogContextMiddleware

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

app.add_middleware(StructlogContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
    allow_credentials=settings.cors.allow_credentials,
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(api_v1_router, prefix=API_V1_PREFIX)
