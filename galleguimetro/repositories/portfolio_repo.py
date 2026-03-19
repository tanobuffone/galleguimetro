import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models.database import Portfolio, OptionPosition
from ..models.schemas import PortfolioCreate, PortfolioUpdate

logger = logging.getLogger(__name__)


async def create_portfolio(db: AsyncSession, data: PortfolioCreate, owner_id: UUID) -> Portfolio:
    portfolio = Portfolio(
        name=data.name,
        description=data.description,
        owner_id=owner_id,
    )
    db.add(portfolio)
    await db.flush()
    await db.refresh(portfolio)
    return portfolio


async def get_portfolio(db: AsyncSession, portfolio_id: UUID, owner_id: UUID) -> Optional[Portfolio]:
    stmt = (
        select(Portfolio)
        .options(selectinload(Portfolio.positions))
        .where(Portfolio.id == portfolio_id, Portfolio.owner_id == owner_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_portfolios(
    db: AsyncSession, owner_id: UUID, page: int = 1, page_size: int = 10
) -> tuple[List[Portfolio], int]:
    # Count
    count_stmt = select(func.count()).select_from(Portfolio).where(Portfolio.owner_id == owner_id)
    total = (await db.execute(count_stmt)).scalar()

    # Items
    stmt = (
        select(Portfolio)
        .options(selectinload(Portfolio.positions))
        .where(Portfolio.owner_id == owner_id)
        .order_by(Portfolio.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    portfolios = list(result.scalars().all())
    return portfolios, total


async def update_portfolio(
    db: AsyncSession, portfolio_id: UUID, owner_id: UUID, data: PortfolioUpdate
) -> Optional[Portfolio]:
    portfolio = await get_portfolio(db, portfolio_id, owner_id)
    if not portfolio:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(portfolio, key, value)

    await db.flush()
    await db.refresh(portfolio)
    return portfolio


async def delete_portfolio(db: AsyncSession, portfolio_id: UUID, owner_id: UUID) -> bool:
    portfolio = await get_portfolio(db, portfolio_id, owner_id)
    if not portfolio:
        return False
    await db.delete(portfolio)
    return True
