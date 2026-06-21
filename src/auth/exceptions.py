from starlette import status

from src.auth.constants import (
    AGENT_REQUIRED_MSG,
    INVALID_CREDENTIALS_MSG,
    INVALID_TOKEN_MSG,
    INVALID_TOKEN_TYPE_MSG,
    REFRESH_TOKEN_MISSING_MSG,
    TOKEN_EXPIRED_MSG,
)
from src.core.exceptions import AppException


class InvalidCredentialsError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = INVALID_CREDENTIALS_MSG


class TokenExpiredError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = TOKEN_EXPIRED_MSG


class InvalidTokenError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = INVALID_TOKEN_MSG


class RefreshTokenMissingError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = REFRESH_TOKEN_MISSING_MSG


class InvalidTokenTypeError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = INVALID_TOKEN_TYPE_MSG


class AgentRequiredError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = AGENT_REQUIRED_MSG
