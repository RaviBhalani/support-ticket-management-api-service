from enum import Enum

# Table
TABLE_NAME = "tickets"
HISTORY_TABLE_NAME = "ticket_history"
TICKET_FK = f"{TABLE_NAME}.id"

# Router
ROUTER_PREFIX = "/tickets"

# OpenAPI
TICKETS_TAG = "Tickets"
TICKETS_TAG_DESCRIPTION = "Ticket management — create, list, retrieve, update, and delete support tickets."


class HistoryEvent(str, Enum):
    CREATION = "CREATION"
    STATUS_CHANGE = "STATUS_CHANGE"


class TicketCategory(str, Enum):
    ACCOUNT = "ACCOUNT"
    PAYMENTS = "PAYMENTS"
    APP_ISSUE = "APP_ISSUE"
    SUGGESTION = "SUGGESTION"
    OTHER = "OTHER"


class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


# Field limits
HISTORY_EVENT_MAX_LENGTH = max(len(e.value) for e in HistoryEvent)
COMMENTS_MAX_LENGTH = 1024
SUBJECT_MAX_LENGTH = 255
DESCRIPTION_MAX_LENGTH = 1024
PRIORITY_MAX_LENGTH = max(len(p.value) for p in TicketPriority)
CATEGORY_MAX_LENGTH = max(len(c.value) for c in TicketCategory)
STATUS_MAX_LENGTH = max(len(s.value) for s in TicketStatus)

# Priority auto-assigned from category on ticket creation; cannot be updated after that
CATEGORY_PRIORITY_MAP: dict[TicketCategory, TicketPriority] = {
    TicketCategory.PAYMENTS: TicketPriority.CRITICAL,
    TicketCategory.ACCOUNT: TicketPriority.HIGH,
    TicketCategory.APP_ISSUE: TicketPriority.MEDIUM,
    TicketCategory.SUGGESTION: TicketPriority.LOW,
    TicketCategory.OTHER: TicketPriority.LOW,
}

# Endpoint paths
CREATE_TICKET_ENDPOINT = ""

# Error messages
CUSTOMER_NOT_FOUND_MSG = "The specified customer does not exist."
INVALID_CUSTOMER_ROLE_MSG = "The specified user is not a customer."

# Templates
TICKET_CREATED_EMAIL_TEMPLATE = "ticket_created.html"

# Log messages
LOG_TICKET_CREATED = "ticket_created"
