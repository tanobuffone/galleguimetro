from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_db
from ..models.database import User
from ..models.schemas import (
    ApiResponse, PaginationParams, PaginatedResponse,
    AlertCreate, AlertUpdate, AlertResponse,
)
from ..services.auth import get_current_user
from ..repositories import alert_repo

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=ApiResponse)
async def create_alert(
    data: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = await alert_repo.create_alert(db, data)
    return ApiResponse(
        success=True,
        message="Alerta creada",
        data=AlertResponse.model_validate(alert).model_dump(),
    )


@router.get("", response_model=ApiResponse)
async def list_alerts(
    portfolio_id: Optional[UUID] = Query(None),
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alerts, total = await alert_repo.list_alerts(db, portfolio_id, params.page, params.page_size)
    items = [AlertResponse.model_validate(a).model_dump() for a in alerts]
    paginated = PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size if total > 0 else 0,
    )
    return ApiResponse(success=True, message="Alertas listadas", data=paginated.model_dump())


@router.get("/{alert_id}", response_model=ApiResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = await alert_repo.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return ApiResponse(
        success=True,
        message="Alerta obtenida",
        data=AlertResponse.model_validate(alert).model_dump(),
    )


@router.put("/{alert_id}", response_model=ApiResponse)
async def update_alert(
    alert_id: UUID,
    data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = await alert_repo.update_alert(db, alert_id, data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return ApiResponse(
        success=True,
        message="Alerta actualizada",
        data=AlertResponse.model_validate(alert).model_dump(),
    )


@router.delete("/{alert_id}", response_model=ApiResponse)
async def delete_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await alert_repo.delete_alert(db, alert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return ApiResponse(success=True, message="Alerta eliminada")
