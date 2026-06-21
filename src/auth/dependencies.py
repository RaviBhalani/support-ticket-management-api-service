from fastapi import Cookie, Depends

from src.auth.constants import ACCESS_TOKEN_COOKIE, ACCESS_TOKEN_TYPE
from src.auth.exceptions import AgentRequiredError, InvalidCredentialsError, InvalidTokenTypeError
from src.auth.utils import decode_token
from src.core.config import settings
from src.core.constants import Environment
from src.users.constants import UserRole
from src.users.dependencies import get_user_repository
from src.users.models import User
from src.users.repository import UserRepository


def is_secure() -> bool:
    return settings.server.environment != Environment.LOCAL


async def get_current_user(
    access_token: str = Cookie(..., alias=ACCESS_TOKEN_COOKIE),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    payload = decode_token(access_token)
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise InvalidTokenTypeError()
    user = await user_repo.get(int(payload["sub"]))
    if not user:
        raise InvalidCredentialsError()
    return user


async def require_authentication(current_user: User = Depends(get_current_user)) -> User:
    return current_user


async def require_agent(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.AGENT:
        raise AgentRequiredError()
    return current_user
