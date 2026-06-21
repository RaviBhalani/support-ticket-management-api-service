from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.constants import ON_DELETE_CASCADE, ON_DELETE_SET_NULL
from src.core.mixins import CreatedAtMixin, TimestampMixin
from src.core.models import Base
from src.tickets.constants import (
    CATEGORY_MAX_LENGTH,
    COMMENTS_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    HISTORY_EVENT_MAX_LENGTH,
    HISTORY_TABLE_NAME,
    PRIORITY_MAX_LENGTH,
    STATUS_MAX_LENGTH,
    SUBJECT_MAX_LENGTH,
    TABLE_NAME,
    TICKET_FK,
    TicketStatus,
)
from src.users.constants import USER_FK


class Ticket(Base, TimestampMixin):
    __tablename__ = TABLE_NAME

    customer: Mapped[int | None] = mapped_column(
        ForeignKey(USER_FK, ondelete=ON_DELETE_SET_NULL)
    )
    agent: Mapped[int | None] = mapped_column(
        ForeignKey(USER_FK, ondelete=ON_DELETE_SET_NULL)
    )
    subject: Mapped[str] = mapped_column(String(SUBJECT_MAX_LENGTH))
    description: Mapped[str] = mapped_column(String(DESCRIPTION_MAX_LENGTH))
    priority: Mapped[str] = mapped_column(String(PRIORITY_MAX_LENGTH))
    category: Mapped[str] = mapped_column(String(CATEGORY_MAX_LENGTH))
    status: Mapped[str] = mapped_column(String(STATUS_MAX_LENGTH), default=TicketStatus.OPEN.value)


class TicketHistory(Base, CreatedAtMixin):
    __tablename__ = HISTORY_TABLE_NAME

    ticket: Mapped[int] = mapped_column(ForeignKey(TICKET_FK, ondelete=ON_DELETE_CASCADE))
    event: Mapped[str] = mapped_column(String(HISTORY_EVENT_MAX_LENGTH))
    comments: Mapped[str | None] = mapped_column(String(COMMENTS_MAX_LENGTH))
