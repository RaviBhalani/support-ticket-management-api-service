from fastapi import APIRouter

from src.auth.constants import AUTH_TAG, ROUTER_PREFIX as AUTH_PREFIX
from src.auth.router import router as auth_router

router = APIRouter()

router.include_router(auth_router, prefix=AUTH_PREFIX, tags=[AUTH_TAG])
