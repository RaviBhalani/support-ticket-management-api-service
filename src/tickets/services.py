import structlog

from src.tickets.constants import CATEGORY_PRIORITY_MAP, LOG_TICKET_CREATED, HistoryEvent, TicketStatus
from src.tickets.exceptions import CustomerNotFoundError, InvalidCustomerRoleError
from src.tickets.models import Ticket, TicketHistory
from src.tickets.repository import TicketHistoryRepository, TicketRepository
from src.tickets.schemas import CreateTicketRequest
from src.tickets.tasks import send_ticket_created_email
from src.users.constants import UserRole
from src.users.models import User
from src.users.repository import UserRepository

logger = structlog.get_logger(__name__)


async def create_ticket(
    repo: TicketRepository,
    history_repo: TicketHistoryRepository,
    user_repo: UserRepository,
    current_user: User,
    data: CreateTicketRequest,
) -> Ticket:
    if current_user.role == UserRole.CUSTOMER:
        customer_id = current_user.id
    else:
        if data.customer_id is None:
            raise CustomerNotFoundError()
        customer = await user_repo.get(data.customer_id)
        if not customer:
            raise CustomerNotFoundError()
        if customer.role != UserRole.CUSTOMER:
            raise InvalidCustomerRoleError()
        customer_id = data.customer_id

    assigned_agent_id = await repo.get_agent_with_fewest_tickets()

    ticket = Ticket(
        customer=customer_id,
        agent=assigned_agent_id,
        subject=data.subject,
        description=data.description,
        category=data.category.value,
        priority=CATEGORY_PRIORITY_MAP[data.category].value,
        status=TicketStatus.OPEN.value,
    )
    await repo.add(ticket)

    history = TicketHistory(
        ticket=ticket.id,
        event=HistoryEvent.CREATION.value,
    )
    await history_repo.add(history)

    send_ticket_created_email.delay(ticket.id)

    logger.info(LOG_TICKET_CREATED, ticket_id=ticket.id, customer_id=ticket.customer)

    return ticket
