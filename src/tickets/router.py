from fastapi import APIRouter, Depends, status

from src.auth.dependencies import require_agent, require_authentication
from src.tickets import services as ticket_service
from src.tickets.constants import CREATE_TICKET_ENDPOINT, GET_TICKET_ENDPOINT, UPDATE_TICKET_ENDPOINT
from src.tickets.dependencies import get_ticket_history_repository, get_ticket_repository
from src.tickets.repository import TicketHistoryRepository, TicketRepository
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
    repo: TicketRepository = Depends(get_ticket_repository),
    history_repo: TicketHistoryRepository = Depends(get_ticket_history_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> AgentTicketResponse | TicketResponse:
    ticket = await ticket_service.create_ticket(repo, history_repo, user_repo, current_user, body)
    if current_user.role == UserRole.AGENT:
        return AgentTicketResponse.model_validate(ticket)
    return TicketResponse.model_validate(ticket)


@router.get(GET_TICKET_ENDPOINT, status_code=status.HTTP_200_OK)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(require_authentication),
    repo: TicketRepository = Depends(get_ticket_repository),
    history_repo: TicketHistoryRepository = Depends(get_ticket_history_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> AgentTicketDetailResponse | TicketDetailResponse:

    ticket, ticket_history, customer_user, agent_user = await ticket_service.get_ticket(
        ticket_id, repo, history_repo, user_repo, current_user
    )
    detail_fields = {
        "history": [TicketHistoryResponse.model_validate(h) for h in ticket_history],
        "customer": TicketUserResponse.model_validate(customer_user) if customer_user else None,
        "agent": TicketUserResponse.model_validate(agent_user) if agent_user else None,
    }

    if current_user.role == UserRole.AGENT:
        return AgentTicketDetailResponse(
            **AgentTicketResponse.model_validate(ticket).model_dump(exclude={"customer", "agent"}),
            **detail_fields,
        )
    return TicketDetailResponse(
        **TicketResponse.model_validate(ticket).model_dump(exclude={"customer", "agent"}),
        **detail_fields,
    )


@router.patch(UPDATE_TICKET_ENDPOINT, status_code=status.HTTP_200_OK)
async def update_ticket(
    ticket_id: int,
    body: UpdateTicketRequest,
    current_user: User = Depends(require_agent),
    repo: TicketRepository = Depends(get_ticket_repository),
    history_repo: TicketHistoryRepository = Depends(get_ticket_history_repository),
) -> AgentTicketResponse:
    ticket = await ticket_service.update_ticket(ticket_id, repo, history_repo, current_user, body)
    return AgentTicketResponse.model_validate(ticket)
