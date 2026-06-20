from fastapi import APIRouter, Cookie, Depends, Response, status

from src.auth.constants import (
    ACCESS_COOKIE_PATH,
    ACCESS_TOKEN_COOKIE,
    CookieSameSite,
    LOGIN_ENDPOINT,
    REFRESH_COOKIE_PATH,
    REFRESH_ENDPOINT,
    REFRESH_TOKEN_COOKIE
)

from src.auth.dependencies import is_secure
from src.auth.schemas import LoginRequest, LoginResponse
from src.auth.services import login_user, refresh_access_token
from src.users.dependencies import get_user_repository
from src.users.repository import UserRepository

router = APIRouter()


@router.post(LOGIN_ENDPOINT, response_model=LoginResponse)
async def login(
    body: LoginRequest,
    response: Response,
    repo: UserRepository = Depends(get_user_repository),
    secure: bool = Depends(is_secure),
) -> LoginResponse:
    user, access_token, refresh_token = await login_user(body.email, body.password, repo)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        samesite=CookieSameSite.STRICT.value,
        secure=secure,
        path=ACCESS_COOKIE_PATH,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite=CookieSameSite.STRICT.value,
        secure=secure,
        path=REFRESH_COOKIE_PATH,
    )
    return LoginResponse.model_validate(user)


@router.post(REFRESH_ENDPOINT, status_code=status.HTTP_204_NO_CONTENT)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_TOKEN_COOKIE),
    secure: bool = Depends(is_secure),
) -> None:
    new_access_token = refresh_access_token(refresh_token)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=new_access_token,
        httponly=True,
        samesite=CookieSameSite.STRICT.value,
        secure=secure,
        path=ACCESS_COOKIE_PATH,
    )
