from datetime import datetime
from typing import ClassVar, Self

from fastapi_filter.contrib.sqlalchemy import Filter
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
from src.tickets.models import Ticket, TicketHistory
from src.users.models import User


class TicketFilter(Filter):
    status__in: list[TicketStatus] | None = None
    category__in: list[TicketCategory] | None = None
    priority__in: list[TicketPriority] | None = None

    class Constants(Filter.Constants):
        model = Ticket


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


class TicketUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str


class TicketDetailResponse(TicketResponse):
    customer: TicketUserResponse | None
    agent: TicketUserResponse | None
    history: list[TicketHistoryResponse]
    _flat_schema: ClassVar[type[TicketResponse]] = TicketResponse

    @classmethod
    def build(
        cls,
        ticket: Ticket,
        history: list[TicketHistory],
        customer_user: User | None,
        agent_user: User | None,
    ) -> Self:
        return cls(
            **cls._flat_schema.model_validate(ticket).model_dump(exclude={"customer", "agent"}),
            customer=TicketUserResponse.model_validate(customer_user) if customer_user else None,
            agent=TicketUserResponse.model_validate(agent_user) if agent_user else None,
            history=[TicketHistoryResponse.model_validate(h) for h in history],
        )


class AgentTicketDetailResponse(TicketDetailResponse, AgentTicketResponse):
    _flat_schema: ClassVar[type[TicketResponse]] = AgentTicketResponse
