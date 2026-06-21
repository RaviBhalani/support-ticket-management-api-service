import structlog

from src.core.celery import app
from src.core.constants import DATETIME_DISPLAY_FORMAT
from src.core.database import sync_session_factory
from src.core.utils import read_template
from src.tickets.constants import LOG_TICKET_CREATED_EMAIL_SENT, TICKET_CREATED_EMAIL_TEMPLATE
from src.tickets.models import Ticket
from src.users.models import User

logger = structlog.get_logger(__name__)


@app.task
def send_ticket_created_email(ticket_id: int) -> None:
    # Ticket and customer data are fetched here inside the task rather than passed
    # from the API. This guarantees data freshness and keeps the API response fast —
    # email sending is intentionally offloaded to Celery so the API never blocks
    # waiting for it. Once an email service is available, pass the rendered HTML
    # to it here.
    with sync_session_factory() as session:
        ticket = session.get(Ticket, ticket_id)
        customer = session.get(User, ticket.customer)

    template = read_template(__file__, TICKET_CREATED_EMAIL_TEMPLATE)

    rendered = (
        template
        .replace("{{first_name}}", customer.first_name)
        .replace("{{ticket_id}}", str(ticket.id))
        .replace("{{subject}}", ticket.subject)
        .replace("{{category}}", ticket.category.replace("_", " ").title())
        .replace("{{status}}", ticket.status.replace("_", " ").title())
        .replace("{{created_ts}}", ticket.created_ts.strftime(DATETIME_DISPLAY_FORMAT))
    )
    _ = rendered
    logger.info(LOG_TICKET_CREATED_EMAIL_SENT, ticket_id=ticket_id, email=customer.email)