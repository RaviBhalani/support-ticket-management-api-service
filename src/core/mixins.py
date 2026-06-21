from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    __abstract__ = True

    created_ts: Mapped[datetime] = mapped_column(server_default=func.now())


class TimestampMixin(CreatedAtMixin):
    __abstract__ = True

    modified_ts: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
