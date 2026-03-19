import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.database import Alert
from ..models.schemas import AlertCreate, AlertUpdate

logger = logging.getLogger(__name__)


async def create_alert(db: AsyncSession, data: AlertCreate) -> Alert:
    alert = Alert(
        portfolio_id=data.portfolio_id,
        strategy_id=data.strategy_id,
        message=data.message,
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


async def get_alert(db: AsyncSession, alert_id: UUID) -> Optional[Alert]:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    return result.scalar_one_or_none()


async def list_alerts(
    db: AsyncSession,
    portfolio_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[List[Alert], int]:
    base = select(Alert)
    count_base = select(func.count()).select_from(Alert)

    if portfolio_id:
        base = base.where(Alert.portfolio_id == portfolio_id)
        count_base = count_base.where(Alert.portfolio_id == portfolio_id)

    total = (await db.execute(count_base)).scalar()

    stmt = base.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    alerts = list(result.scalars().all())
    return alerts, total


async def update_alert(db: AsyncSession, alert_id: UUID, data: AlertUpdate) -> Optional[Alert]:
    alert = await get_alert(db, alert_id)
    if not alert:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if update_data.get("condition_met") and not alert.condition_met:
        alert.triggered_at = datetime.utcnow()

    for key, value in update_data.items():
        setattr(alert, key, value)

    await db.flush()
    await db.refresh(alert)
    return alert


async def delete_alert(db: AsyncSession, alert_id: UUID) -> bool:
    alert = await get_alert(db, alert_id)
    if not alert:
        return False
    await db.delete(alert)
    return True
