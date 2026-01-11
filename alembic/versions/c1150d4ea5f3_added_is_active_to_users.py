"""added is_active to users

Revision ID: c1150d4ea5f3
Revises: 4773ca3c8cd2
Create Date: 2026-01-10 21:17:51.984797

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1150d4ea5f3'
down_revision: Union[str, None] = '4773ca3c8cd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
