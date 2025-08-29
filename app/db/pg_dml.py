from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Any, Optional, Type, Sequence
from sqlalchemy import exc, select
from sqlalchemy.orm import InstrumentedAttribute
from app.core.logger import Logger

T = TypeVar("T", bound=object)

logger = Logger.get_logger(__name__)

async def insert_record(
    session: AsyncSession,
    model_instance: T,
) -> T:
    try:
        session.add(model_instance)
        await session.commit()
        await session.refresh(model_instance)
        return model_instance
    except exc.SQLAlchemyError as e:
        await session.rollback()
        logger.exception("Failed to insert record")
        raise

async def upsert_record(session: AsyncSession, instance: T) -> T:
    try:
        merged = await session.merge(instance)
        await session.commit()
        return merged
    except Exception:
        await session.rollback()
        logger.exception("Failed to upsert record")
        raise


async def get_by_id(
    session: AsyncSession,
    model_instance: T,
    pk: Any,  # tuple for composite PKs
) -> Optional[T]:
    """
    Fast path using the identity map; returns None if not found.
    For composite PKs, pass a tuple in PK column order.
    """
    return await session.get(model_instance, pk)

async def get_many(
    session: AsyncSession,
    model: Type[T],
    *,
    filters: dict[str, Any] | None = None,
    order_by: Sequence[InstrumentedAttribute] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[T]:
    """
    Flexible list fetch with optional filters, ordering, paging.
    """
    stmt = select(model)
    if filters:
        for k, v in filters.items():
            stmt = stmt.where(getattr(model, k) == v)
    if order_by:
        stmt = stmt.order_by(*order_by)
    if limit is not None:
        stmt = stmt.limit(limit)
    if offset is not None:
        stmt = stmt.offset(offset)

    result = await session.execute(stmt)
    return list(result.scalars().all())

async def get_one(
    session: AsyncSession,
    model: Type[T],
    **filters: Any,
) -> Optional[T]:
    """
    Fetch exactly one (or None) using equality filters.
    Example: await get_one(session, User, email="a@b.com")
    """
    stmt = select(model)
    for name, value in filters.items():
        stmt = stmt.where(getattr(model, name) == value)
    result = await session.execute(stmt.limit(1))
    return result.scalars().first()