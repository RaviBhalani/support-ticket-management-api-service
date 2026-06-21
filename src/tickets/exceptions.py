from starlette import status

from src.core.exceptions import AppException
from src.tickets.constants import (
    CUSTOMER_NOT_FOUND_MSG,
    INVALID_CUSTOMER_ROLE_MSG,
    INVALID_STATUS_TRANSITION_MSG,
    TICKET_ACCESS_DENIED_MSG,
    TICKET_LOCKED_MSG,
    TICKET_NOT_ASSIGNED_MSG,
    TICKET_NOT_DELETABLE_MSG,
    TICKET_NOT_FOUND_MSG,
)


class CustomerNotFoundError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = CUSTOMER_NOT_FOUND_MSG


class InvalidCustomerRoleError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = INVALID_CUSTOMER_ROLE_MSG


class TicketNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = TICKET_NOT_FOUND_MSG


class TicketNotAssignedError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = TICKET_NOT_ASSIGNED_MSG


class InvalidStatusTransitionError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = INVALID_STATUS_TRANSITION_MSG


class TicketAccessDeniedError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = TICKET_ACCESS_DENIED_MSG


class TicketLockedError(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = TICKET_LOCKED_MSG


class TicketNotDeletableError(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = TICKET_NOT_DELETABLE_MSG
