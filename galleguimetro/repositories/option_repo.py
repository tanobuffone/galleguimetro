import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.database import Option, Underlying
from ..models.schemas import OptionCreate, OptionUpdate

logger = logging.getLogger(__name__)


async def get_or_create_underlying(db: AsyncSession, symbol: str) -> Underlying:
    """Obtiene o crea un activo subyacente por símbolo."""
    result = await db.execute(select(Underlying).where(Underlying.symbol == symbol))
    underlying = result.scalar_one_or_none()
    if not underlying:
        underlying = Underlying(symbol=symbol, name=symbol)
        db.add(underlying)
        await db.flush()
        await db.refresh(underlying)
    return underlying


async def create_option(db: AsyncSession, data: OptionCreate) -> Option:
    underlying = await get_or_create_underlying(db, data.underlying_symbol)

    option = Option(
        symbol=data.symbol,
        underlying_id=underlying.id,
        option_type=data.option_type.value,
        strike_price=data.strike_price,
        expiration_date=data.expiration_date,
        implied_volatility=data.implied_volatility,
        dividend_yield=data.dividend_yield or 0.0,
        risk_free_rate=data.risk_free_rate or 0.0,
        last_price=data.last_price,
        bid=data.bid,
        ask=data.ask,
    )
    db.add(option)
    await db.flush()
    await db.refresh(option)
    return option


async def get_option(db: AsyncSession, option_id: UUID) -> Optional[Option]:
    result = await db.execute(select(Option).where(Option.id == option_id))
    return result.scalar_one_or_none()


async def get_option_by_symbol(db: AsyncSession, symbol: str) -> Optional[Option]:
    result = await db.execute(select(Option).where(Option.symbol == symbol))
    return result.scalar_one_or_none()


async def list_options(
    db: AsyncSession, page: int = 1, page_size: int = 50
) -> tuple[List[Option], int]:
    count_stmt = select(func.count()).select_from(Option)
    total = (await db.execute(count_stmt)).scalar()

    stmt = (
        select(Option)
        .order_by(Option.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    options = list(result.scalars().all())
    return options, total


async def get_option_chain(db: AsyncSession, underlying_symbol: str) -> List[Option]:
    underlying = await db.execute(
        select(Underlying).where(Underlying.symbol == underlying_symbol)
    )
    u = underlying.scalar_one_or_none()
    if not u:
        return []

    result = await db.execute(
        select(Option)
        .where(Option.underlying_id == u.id)
        .order_by(Option.strike_price, Option.expiration_date)
    )
    return list(result.scalars().all())


async def update_option(db: AsyncSession, option_id: UUID, data: OptionUpdate) -> Optional[Option]:
    option = await get_option(db, option_id)
    if not option:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(option, key, value)

    await db.flush()
    await db.refresh(option)
    return option


async def delete_option(db: AsyncSession, option_id: UUID) -> bool:
    option = await get_option(db, option_id)
    if not option:
        return False
    await db.delete(option)
    return True
