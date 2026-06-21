from fastapi import APIRouter, Depends, status

from src.auth.dependencies import require_authentication
from src.tickets import services as ticket_service
from src.tickets.constants import CREATE_TICKET_ENDPOINT
from src.tickets.dependencies import get_ticket_history_repository, get_ticket_repository
from src.tickets.repository import TicketHistoryRepository, TicketRepository
from src.tickets.schemas import AgentTicketResponse, CreateTicketRequest, TicketResponse
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
