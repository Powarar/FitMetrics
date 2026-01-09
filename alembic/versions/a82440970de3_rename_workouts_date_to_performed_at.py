"""rename workouts.date to performed_at

Revision ID: a82440970de3
Revises: 4efa156ed8ec
Create Date: 2026-01-09 20:32:59.368274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a82440970de3'
down_revision: Union[str, None] = '4efa156ed8ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "workouts",
        "date",
        new_column_name="performed_at",
    )


def downgrade() -> None:
    op.alter_column(
        "workouts",
        "performed_at",
        new_column_name="date",
    )