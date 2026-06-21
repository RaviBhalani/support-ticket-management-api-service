from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.tickets.constants import (
    DESCRIPTION_MAX_LENGTH,
    SUBJECT_MAX_LENGTH,
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


class CreateTicketRequest(BaseModel):
    subject: str = Field(max_length=SUBJECT_MAX_LENGTH)
    description: str = Field(max_length=DESCRIPTION_MAX_LENGTH)
    category: TicketCategory
    customer_id: int | None = None


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
