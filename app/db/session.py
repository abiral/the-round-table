"""Async engine + session factory.

The engine is module-global and reused for the process lifetime. Sessions are
short-lived and created per request via `get_session()` (FastAPI dependency).
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def _database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Set it in backend/.env or via docker-compose."
        )
    return url


engine = create_async_engine(_database_url(), future=True, echo=False, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a transactional async session."""
    async with async_session_maker() as session:
        yield session
