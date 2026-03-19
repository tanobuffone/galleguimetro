import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models.database import OptionPosition, Portfolio, PositionStatusDB
from ..models.schemas import PositionCreate, PositionUpdate

logger = logging.getLogger(__name__)


async def add_position(
    db: AsyncSession, portfolio_id: UUID, owner_id: UUID, data: PositionCreate
) -> Optional[OptionPosition]:
    # Verificar que el portfolio pertenece al usuario
    stmt = select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.owner_id == owner_id)
    result = await db.execute(stmt)
    portfolio = result.scalar_one_or_none()
    if not portfolio:
        return None

    position = OptionPosition(
        portfolio_id=portfolio_id,
        option_id=data.option_id,
        quantity=data.quantity,
        entry_price=data.entry_price,
        current_price=data.current_price,
        fees=data.fees or 0.0,
    )
    # Calcular market_value y unrealized_pnl
    if data.current_price and data.entry_price:
        position.market_value = data.current_price * data.quantity
        position.unrealized_pnl = (data.current_price - data.entry_price) * data.quantity

    db.add(position)
    await db.flush()
    await db.refresh(position)
    return position


async def update_position(
    db: AsyncSession, position_id: UUID, owner_id: UUID, data: PositionUpdate
) -> Optional[OptionPosition]:
    stmt = (
        select(OptionPosition)
        .join(Portfolio)
        .where(OptionPosition.id == position_id, Portfolio.owner_id == owner_id)
    )
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()
    if not position:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Manejar cambio de estado a CLOSED
    if update_data.get("status") == "closed":
        update_data["exit_date"] = datetime.utcnow()
        if position.entry_price and position.current_price:
            position.realized_pnl = (position.current_price - position.entry_price) * position.quantity

    for key, value in update_data.items():
        setattr(position, key, value)

    # Recalcular market_value y unrealized_pnl
    if position.current_price and position.entry_price:
        position.market_value = position.current_price * position.quantity
        position.unrealized_pnl = (position.current_price - position.entry_price) * position.quantity

    await db.flush()
    await db.refresh(position)
    return position


async def remove_position(db: AsyncSession, position_id: UUID, owner_id: UUID) -> bool:
    stmt = (
        select(OptionPosition)
        .join(Portfolio)
        .where(OptionPosition.id == position_id, Portfolio.owner_id == owner_id)
    )
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()
    if not position:
        return False
    await db.delete(position)
    return True
