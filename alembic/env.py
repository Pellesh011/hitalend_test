import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# =========================
# Alembic Config
# =========================
config = context.config

# =========================
# Logging
# =========================
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import logging

logger = logging.getLogger("alembic.env")

# =========================
# Import models (CRITICAL)
# =========================
from app.db.base import Base
import app.models  # noqa: F401  <-- регистрирует все модели

target_metadata = Base.metadata


# =========================
# Offline migrations
# =========================
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    logger.info("Running OFFLINE migrations")
    logger.info(f"DB URL: {url}")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# =========================
# Online migrations (async)
# =========================
def do_run_migrations(connection: Connection) -> None:
    logger.info("Configuring migration context (ONLINE)")

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=False,
    )

    with context.begin_transaction():
        logger.info("Starting migration transaction")
        context.run_migrations()
        logger.info("Migration transaction completed")


async def run_migrations_online_async() -> None:
    logger.info("Creating async engine for migrations")

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        logger.info("Database connection established")

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()
    logger.info("Engine disposed")


def run_migrations_online() -> None:
    logger.info("RUN MIGRATIONS ONLINE (ASYNC MODE)")

    asyncio.run(run_migrations_online_async())


# =========================
# Entry point
# =========================
if context.is_offline_mode():
    logger.info("Alembic running in OFFLINE mode")
    run_migrations_offline()
else:
    logger.info("Alembic running in ONLINE mode")
    run_migrations_online()