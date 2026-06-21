from fastapi import APIRouter

from src.auth.constants import AUTH_TAG, ROUTER_PREFIX as AUTH_PREFIX
from src.auth.router import router as auth_router
from src.tickets.constants import ROUTER_PREFIX as TICKETS_PREFIX, TICKETS_TAG
from src.tickets.router import router as tickets_router

router = APIRouter()

router.include_router(auth_router, prefix=AUTH_PREFIX, tags=[AUTH_TAG])
router.include_router(tickets_router, prefix=TICKETS_PREFIX, tags=[TICKETS_TAG])
