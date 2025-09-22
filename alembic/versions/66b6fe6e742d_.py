"""empty message

Revision ID: 66b6fe6e742d
Revises: 79ea903ece17
Create Date: 2025-09-22 12:33:23.212920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66b6fe6e742d'
down_revision: Union[str, Sequence[str], None] = '79ea903ece17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
