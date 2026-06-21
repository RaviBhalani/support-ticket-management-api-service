from starlette import status

from src.core.exceptions import AppException
from src.tickets.constants import CUSTOMER_NOT_FOUND_MSG, INVALID_CUSTOMER_ROLE_MSG


class CustomerNotFoundError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = CUSTOMER_NOT_FOUND_MSG


class InvalidCustomerRoleError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = INVALID_CUSTOMER_ROLE_MSG
