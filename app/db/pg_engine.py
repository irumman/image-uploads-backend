from app.configs.settings import settings
from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.logger import logger


class PgEngine:
    def __init__(self):
        conn_str = (f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:"
                    f"{settings.postgres_port}/{settings.postgres_dbname}")
        self._engine = create_async_engine(conn_str)
        self._sessionmaker = async_sessionmaker(bind=self._engine, expire_on_commit=False)


    async def close(self):
        if self._engine is None:
            raise Exception("Postgres Engine is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                logger.exception("Database connection context failed")
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception("Database session context failed")
                raise
            finally:
                await session.close()


sessionmanager = PgEngine()

# For dependency injection
async def get_db_session():
    async with sessionmanager.session() as session:
        yield session

