# START_MODULE_CONTRACT
#   PURPOSE: Async engine, session factory and the FastAPI session dependency.
#   SCOPE: Database connectivity only; no queries.
#   DEPENDS: M-BACKEND-CORE
#   LINKS: M-DB, V-M-DB
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   engine - process-wide AsyncEngine
#   SessionLocal - async_sessionmaker bound to engine
#   get_session - FastAPI dependency yielding an AsyncSession
# END_MODULE_MAP
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# START_CONTRACT: get_session
#   PURPOSE: Provide one AsyncSession per request.
#   INPUTS: none
#   OUTPUTS: { AsyncIterator[AsyncSession] - session closed after the request }
#   SIDE_EFFECTS: opens a pooled DB connection lazily
# END_CONTRACT: get_session
async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
