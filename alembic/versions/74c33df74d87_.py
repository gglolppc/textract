"""empty message

Revision ID: 74c33df74d87
Revises: 346c60ea4e7e
Create Date: 2025-09-29 15:57:47.579654

"""
from typing import Sequence, Union
from sqlalchemy.sql import text
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '74c33df74d87'
down_revision: Union[str, Sequence[str], None] = '346c60ea4e7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "users",
        "created_at",
        server_default=text("NOW()"),
        existing_type=sa.TIMESTAMP(timezone=True),
    )
    op.alter_column(
        "users",
        "updated_at",
        server_default=text("NOW()"),
        existing_type=sa.TIMESTAMP(timezone=True),
    )


def downgrade():
    op.alter_column(
        "users",
        "created_at",
        server_default=None,
        existing_type=sa.TIMESTAMP(timezone=True),
    )
    op.alter_column(
        "users",
        "updated_at",
        server_default=None,
        existing_type=sa.TIMESTAMP(timezone=True),
    )