from fastapi import APIRouter, Depends, status

from src.auth.dependencies import require_agent, require_authentication
from src.tickets import services as ticket_service
from src.tickets.constants import CREATE_TICKET_ENDPOINT, GET_TICKET_ENDPOINT, UPDATE_TICKET_ENDPOINT
from src.tickets.dependencies import get_ticket_history_repository, get_ticket_repository
from src.tickets.repository import TicketHistoryRepository, TicketRepository
from src.tickets.dependencies import TicketDependencies
from src.tickets.schemas import (
    AgentTicketDetailResponse,
    AgentTicketResponse,
    CreateTicketRequest,
    TicketDetailResponse,
    TicketHistoryResponse,
    TicketResponse,
    TicketUserResponse,
    UpdateTicketRequest,
)
from src.users.constants import UserRole
from src.users.dependencies import get_user_repository
from src.users.models import User
from src.users.repository import UserRepository

router = APIRouter()


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
