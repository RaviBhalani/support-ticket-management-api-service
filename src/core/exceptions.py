from starlette import status

from src.core.constants import DEFAULT_ERROR_MSG


class AppException(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = DEFAULT_ERROR_MSG

    def __init__(self) -> None:
        super().__init__(self.detail)
