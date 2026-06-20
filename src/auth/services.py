from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.auth.constants import ACCESS_TOKEN_TYPE, ALGORITHM, REFRESH_TOKEN_TYPE
from src.auth.exceptions import InvalidCredentialsError, InvalidTokenError, InvalidTokenTypeError, RefreshTokenMissingError, TokenExpiredError
from src.core.config import settings
from src.users.models import User
from src.users.repository import UserRepository

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire, "type": ACCESS_TOKEN_TYPE}
    return jwt.encode(payload, settings.jwt.private_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt.refresh_token_expire_days)
    payload = {"sub": str(user_id), "exp": expire, "type": REFRESH_TOKEN_TYPE}
    return jwt.encode(payload, settings.jwt.private_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt.public_key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()


async def login_user(email: str, password: str, repo: UserRepository) -> tuple[User, str, str]:
    user = await repo.get_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()
    return user, create_access_token(user.id), create_refresh_token(user.id)


def refresh_access_token(token: str | None) -> str:
    if not token:
        raise RefreshTokenMissingError()
    payload = decode_token(token)
    if payload.get("type") != REFRESH_TOKEN_TYPE:
        raise InvalidTokenTypeError()
    return create_access_token(int(payload["sub"]))
