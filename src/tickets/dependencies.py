from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.tickets.repository import TicketHistoryRepository, TicketRepository
from src.users.dependencies import get_user_repository
from src.users.repository import UserRepository


def get_ticket_repository(session: AsyncSession = Depends(get_session)) -> TicketRepository:
    return TicketRepository(session)


def get_ticket_history_repository(
    session: AsyncSession = Depends(get_session),
) -> TicketHistoryRepository:
    return TicketHistoryRepository(session)


class TicketDependencies:

    def __init__(
        self,
        repo: TicketRepository = Depends(get_ticket_repository),
        history_repo: TicketHistoryRepository = Depends(get_ticket_history_repository),
        user_repo: UserRepository = Depends(get_user_repository),
    ) -> None:
        self.repo = repo
        self.history_repo = history_repo
        self.user_repo = user_repo
