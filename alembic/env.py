from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.db.database import Base, RequestLog, Feedback

# Эта переменная нужна для автогенерации
target_metadata = Base.metadata

# URL БД (sync, для alembic)
DB_URL = settings.database_alembic_url

# Конфиг Alembic
config = context.config
config.set_main_option("sqlalchemy.url", DB_URL)

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline():
    """Запуск миграций без подключения к базе"""
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 👈 следит за изменениями типов
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запуск миграций с подключением к базе"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 👈 тоже следим за изменениями
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
