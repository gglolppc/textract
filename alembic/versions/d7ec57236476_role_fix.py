from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "d7ec57236476"
down_revision: Union[str, Sequence[str], None] = "d523682744ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = sa.Enum("user", "admin", "moderator", name="role_enum")

def upgrade() -> None:
    # создаём ENUM-тип
    role_enum.create(op.get_bind(), checkfirst=True)

    # меняем колонку, указывая явное преобразование
    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(),
        type_=role_enum,
        existing_nullable=False,
        postgresql_using="role::role_enum"
    )

def downgrade() -> None:
    # обратно в строку
    op.alter_column(
        "users",
        "role",
        existing_type=role_enum,
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="role::text"
    )

    # удаляем ENUM-тип
    role_enum.drop(op.get_bind(), checkfirst=True)
