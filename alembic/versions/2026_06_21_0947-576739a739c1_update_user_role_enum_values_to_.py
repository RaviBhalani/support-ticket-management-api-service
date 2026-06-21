"""update user role enum values to uppercase

Revision ID: 576739a739c1
Revises: 22ad19280549
Create Date: 2026-06-21 09:47:17.547894+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '576739a739c1'
down_revision: Union[str, Sequence[str], None] = '22ad19280549'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE users SET role = 'AGENT' WHERE role = 'agent'")
    op.execute("UPDATE users SET role = 'CUSTOMER' WHERE role = 'customer'")


def downgrade() -> None:
    op.execute("UPDATE users SET role = 'agent' WHERE role = 'AGENT'")
    op.execute("UPDATE users SET role = 'customer' WHERE role = 'CUSTOMER'")
