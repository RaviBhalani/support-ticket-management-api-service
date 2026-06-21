import jwt

from src.auth.constants import ALGORITHM
from src.auth.exceptions import InvalidTokenError, TokenExpiredError
from src.core.config import settings


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt.public_key, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()
