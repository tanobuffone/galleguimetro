from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_db
from ..models.database import User
from ..models.schemas import (
    ApiResponse, PaginationParams, PaginatedResponse,
    StrategyCreate, StrategyUpdate, StrategyResponse,
)
from ..services.auth import get_current_user
from ..repositories import strategy_repo

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.post("", response_model=ApiResponse)
async def create_strategy(
    data: StrategyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_repo.create_strategy(db, data, current_user.id)
    if not strategy:
        raise HTTPException(status_code=400, detail="No se pudo crear la estrategia")
    return ApiResponse(
        success=True,
        message="Estrategia creada",
        data=StrategyResponse.model_validate(strategy).model_dump(),
    )


@router.get("", response_model=ApiResponse)
async def list_strategies(
    portfolio_id: Optional[UUID] = Query(None),
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategies, total = await strategy_repo.list_strategies(
        db, portfolio_id, params.page, params.page_size
    )
    items = [StrategyResponse.model_validate(s).model_dump() for s in strategies]
    paginated = PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size if total > 0 else 0,
    )
    return ApiResponse(success=True, message="Estrategias listadas", data=paginated.model_dump())


@router.get("/{strategy_id}", response_model=ApiResponse)
async def get_strategy(
    strategy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_repo.get_strategy(db, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Estrategia no encontrada")
    return ApiResponse(
        success=True,
        message="Estrategia obtenida",
        data=StrategyResponse.model_validate(strategy).model_dump(),
    )


@router.put("/{strategy_id}", response_model=ApiResponse)
async def update_strategy(
    strategy_id: UUID,
    data: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_repo.update_strategy(db, strategy_id, data)
    if not strategy:
        raise HTTPException(status_code=404, detail="Estrategia no encontrada")
    return ApiResponse(
        success=True,
        message="Estrategia actualizada",
        data=StrategyResponse.model_validate(strategy).model_dump(),
    )


@router.delete("/{strategy_id}", response_model=ApiResponse)
async def delete_strategy(
    strategy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await strategy_repo.delete_strategy(db, strategy_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Estrategia no encontrada")
    return ApiResponse(success=True, message="Estrategia eliminada")
