# START_MODULE_CONTRACT
#   PURPOSE: Alembic migration environment (async engine, app metadata).
#   SCOPE: Online and offline migration runs.
#   DEPENDS: M-BACKEND-CORE
#   LINKS: M-DB, V-M-DB
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   config                 - Alembic config object
#   target_metadata        - metadata of all ORM models
#   DATABASE_URL           - DSN from app settings
#   run_migrations_offline - emit SQL without a DB connection
#   run_migrations_online  - apply migrations through the async engine
# END_MODULE_MAP
import asyncio

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app import models  # noqa: F401  (register tables on metadata)
from app.core.config import get_settings
from app.db.base import Base

config = context.config
target_metadata = Base.metadata
DATABASE_URL = get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def _do_run(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as connection:
        await connection.run_sync(_do_run)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
