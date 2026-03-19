import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models.database import Strategy, StrategyLeg, Underlying, Portfolio
from ..models.schemas import StrategyCreate, StrategyUpdate

logger = logging.getLogger(__name__)


async def create_strategy(db: AsyncSession, data: StrategyCreate, owner_id: UUID) -> Optional[Strategy]:
    # Obtener underlying
    result = await db.execute(select(Underlying).where(Underlying.symbol == data.underlying_symbol))
    underlying = result.scalar_one_or_none()
    if not underlying:
        underlying = Underlying(symbol=data.underlying_symbol, name=data.underlying_symbol)
        db.add(underlying)
        await db.flush()

    # Verificar portfolio si se especifica
    if data.portfolio_id:
        p_result = await db.execute(
            select(Portfolio).where(Portfolio.id == data.portfolio_id, Portfolio.owner_id == owner_id)
        )
        if not p_result.scalar_one_or_none():
            return None

    strategy = Strategy(
        strategy_type=data.strategy_type.value,
        name=data.name,
        description=data.description,
        portfolio_id=data.portfolio_id,
        underlying_id=underlying.id,
    )
    db.add(strategy)
    await db.flush()

    # Crear legs
    for leg_data in data.legs:
        leg = StrategyLeg(
            strategy_id=strategy.id,
            option_id=leg_data.option_id,
            quantity=leg_data.quantity,
            action=leg_data.action,
        )
        db.add(leg)

    await db.flush()
    await db.refresh(strategy)
    return strategy


async def get_strategy(db: AsyncSession, strategy_id: UUID) -> Optional[Strategy]:
    stmt = (
        select(Strategy)
        .options(selectinload(Strategy.legs))
        .where(Strategy.id == strategy_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_strategies(
    db: AsyncSession,
    portfolio_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[List[Strategy], int]:
    base = select(Strategy)
    count_base = select(func.count()).select_from(Strategy)

    if portfolio_id:
        base = base.where(Strategy.portfolio_id == portfolio_id)
        count_base = count_base.where(Strategy.portfolio_id == portfolio_id)

    total = (await db.execute(count_base)).scalar()

    stmt = (
        base
        .options(selectinload(Strategy.legs))
        .order_by(Strategy.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    strategies = list(result.scalars().all())
    return strategies, total


async def update_strategy(db: AsyncSession, strategy_id: UUID, data: StrategyUpdate) -> Optional[Strategy]:
    strategy = await get_strategy(db, strategy_id)
    if not strategy:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(strategy, key, value)

    await db.flush()
    await db.refresh(strategy)
    return strategy


async def delete_strategy(db: AsyncSession, strategy_id: UUID) -> bool:
    strategy = await get_strategy(db, strategy_id)
    if not strategy:
        return False
    await db.delete(strategy)
    return True
