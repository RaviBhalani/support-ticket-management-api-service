from fastapi import APIRouter, Depends, status
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from src.auth.dependencies import require_agent, require_authentication, require_customer
from src.tickets import services as ticket_service
from src.tickets.constants import (
    CREATE_TICKET_ENDPOINT,
    DELETE_TICKET_ENDPOINT,
    GET_TICKET_ENDPOINT,
    LIST_TICKETS_ENDPOINT,
    UPDATE_TICKET_ENDPOINT,
)
from src.tickets.dependencies import TicketDependencies
from src.tickets.schemas import (
    AgentTicketDetailResponse,
    AgentTicketResponse,
    CreateTicketRequest,
    TicketDetailResponse,
    TicketFilter,
    TicketResponse,
    UpdateTicketRequest,
)
from src.users.constants import UserRole
from src.users.models import User

router = APIRouter()


@router.get(LIST_TICKETS_ENDPOINT, status_code=status.HTTP_200_OK)
async def list_tickets(
    ticket_filter: TicketFilter = FilterDepends(TicketFilter),
    params: Params = Depends(),
    current_user: User = Depends(require_authentication),
    deps: TicketDependencies = Depends(),
) -> Page[AgentTicketResponse] | Page[TicketResponse]:
    query = ticket_service.list_tickets(deps.repo, current_user, ticket_filter)
    schema = AgentTicketResponse if current_user.role == UserRole.AGENT else TicketResponse
    return await paginate(
        deps.session,
        query,
        params=params,
        transformer=lambda items: [schema.model_validate(t) for t in items],
    )


@router.post(CREATE_TICKET_ENDPOINT, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    body: CreateTicketRequest,
    current_user: User = Depends(require_authentication),
    deps: TicketDependencies = Depends(),
) -> AgentTicketResponse | TicketResponse:
    ticket = await ticket_service.create_ticket(deps.repo, deps.history_repo, deps.user_repo, current_user, body)
    if current_user.role == UserRole.AGENT:
        return AgentTicketResponse.model_validate(ticket)
    return TicketResponse.model_validate(ticket)


@router.get(GET_TICKET_ENDPOINT, status_code=status.HTTP_200_OK)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(require_authentication),
    deps: TicketDependencies = Depends(),
) -> AgentTicketDetailResponse | TicketDetailResponse:
    ticket, ticket_history, customer_user, agent_user = await ticket_service.get_ticket(
        ticket_id, deps.repo, deps.history_repo, deps.user_repo, current_user
    )
    if current_user.role == UserRole.AGENT:
        return AgentTicketDetailResponse.build(ticket, ticket_history, customer_user, agent_user)
    return TicketDetailResponse.build(ticket, ticket_history, customer_user, agent_user)


@router.patch(UPDATE_TICKET_ENDPOINT, status_code=status.HTTP_200_OK)
async def update_ticket(
    ticket_id: int,
    body: UpdateTicketRequest,
    current_user: User = Depends(require_agent),
    deps: TicketDependencies = Depends(),
) -> AgentTicketResponse:
    ticket = await ticket_service.update_ticket(ticket_id, deps.repo, deps.history_repo, current_user, body)
    return AgentTicketResponse.model_validate(ticket)


@router.delete(DELETE_TICKET_ENDPOINT, status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(require_customer),
    deps: TicketDependencies = Depends(),
) -> None:
    await ticket_service.delete_ticket(ticket_id, deps.repo, current_user)
