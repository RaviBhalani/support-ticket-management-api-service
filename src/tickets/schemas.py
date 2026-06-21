from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.tickets.constants import (
    COMMENTS_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    SUBJECT_MAX_LENGTH,
    HistoryEvent,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


class CreateTicketRequest(BaseModel):
    subject: str = Field(max_length=SUBJECT_MAX_LENGTH)
    description: str = Field(max_length=DESCRIPTION_MAX_LENGTH)
    category: TicketCategory
    customer_id: int | None = None


class UpdateTicketRequest(BaseModel):
    category: TicketCategory | None = None
    status: TicketStatus | None = None
    comments: str | None = Field(default=None, max_length=COMMENTS_MAX_LENGTH)


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer: int | None
    agent: int | None
    subject: str
    description: str
    category: TicketCategory
    status: TicketStatus
    created_ts: datetime
    modified_ts: datetime


class AgentTicketResponse(TicketResponse):
    priority: TicketPriority


class TicketHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket: int
    event: HistoryEvent
    comments: str | None
    created_ts: datetime


class TicketDetailResponse(TicketResponse):
    history: list[TicketHistoryResponse]


class AgentTicketDetailResponse(AgentTicketResponse):
    history: list[TicketHistoryResponse]
