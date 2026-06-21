from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.tickets.repository import TicketHistoryRepository, TicketRepository


def get_ticket_repository(session: AsyncSession = Depends(get_session)) -> TicketRepository:
    return TicketRepository(session)


def get_ticket_history_repository(
    session: AsyncSession = Depends(get_session),
) -> TicketHistoryRepository:
    return TicketHistoryRepository(session)
