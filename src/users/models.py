from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import Base
from src.users.constants import (
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    TABLE_NAME,
    UserRole,
)


class User(Base):
    __tablename__ = TABLE_NAME

    first_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH))
    last_name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH))
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(PASSWORD_MAX_LENGTH))
    role: Mapped[UserRole] = mapped_column(String(ROLE_MAX_LENGTH))
