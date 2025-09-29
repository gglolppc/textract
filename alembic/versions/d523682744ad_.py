"""empty message

Revision ID: d523682744ad
Revises: 74c33df74d87
Create Date: 2025-09-29 16:31:02.492453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd523682744ad'
down_revision: Union[str, Sequence[str], None] = '74c33df74d87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.alter_column(
        "users",
        "usage_reset_at",
        server_default=sa.text("timezone('utc', now())"),
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "usage_reset_at",
        server_default=None,
    )