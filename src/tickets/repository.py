from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.tickets.models import Ticket, TicketHistory
from src.users.constants import UserRole
from src.users.models import User


class TicketRepository(BaseRepository[Ticket]):
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Ticket, session)

    async def get_agent_with_fewest_tickets(self) -> int:
        counts_sq = (
            select(
                User.id.label("agent_id"),
                func.count(Ticket.id).label("ticket_count")
            )
            .outerjoin(Ticket, Ticket.agent == User.id)
            .where(User.role == UserRole.AGENT)
            .group_by(User.id)
            .subquery()
        )
        min_count_sq = select(func.min(counts_sq.c.ticket_count)).scalar_subquery()
        result = await self._session.execute(
            select(counts_sq.c.agent_id)
            .where(counts_sq.c.ticket_count == min_count_sq)
            .order_by(func.random())
            .limit(1)
        )
        return result.scalar_one()


class TicketHistoryRepository(BaseRepository[TicketHistory]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TicketHistory, session)
