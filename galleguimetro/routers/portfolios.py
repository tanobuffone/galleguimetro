from uuid import UUID
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_db
from ..models.database import User, Portfolio, OptionPosition
from ..models.schemas import (
    ApiResponse, PaginationParams, PaginatedResponse,
    PortfolioCreate, PortfolioUpdate,
    PositionCreate, PositionUpdate,
)
from ..services.auth import get_current_user
from ..repositories import portfolio_repo, position_repo

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


def serialize_position(pos: OptionPosition) -> Dict[str, Any]:
    return {
        "id": str(pos.id),
        "portfolio_id": str(pos.portfolio_id),
        "option_id": str(pos.option_id),
        "quantity": pos.quantity,
        "entry_price": pos.entry_price,
        "current_price": pos.current_price,
        "market_value": pos.market_value,
        "unrealized_pnl": pos.unrealized_pnl,
        "realized_pnl": pos.realized_pnl or 0.0,
        "status": pos.status.value if hasattr(pos.status, 'value') else str(pos.status),
        "entry_date": pos.entry_date.isoformat() if pos.entry_date else None,
        "exit_date": pos.exit_date.isoformat() if pos.exit_date else None,
        "fees": pos.fees or 0.0,
        "created_at": pos.created_at.isoformat() if pos.created_at else None,
        "updated_at": pos.updated_at.isoformat() if pos.updated_at else None,
    }


def serialize_portfolio(p: Portfolio, include_positions: bool = False) -> Dict[str, Any]:
    data = {
        "id": str(p.id),
        "name": p.name,
        "description": p.description,
        "owner_id": str(p.owner_id) if p.owner_id else None,
        "total_market_value": p.total_market_value or 0.0,
        "total_unrealized_pnl": p.total_unrealized_pnl or 0.0,
        "total_realized_pnl": p.total_realized_pnl or 0.0,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }
    if include_positions:
        # positions ya fue eager-loaded por selectinload
        data["positions"] = [serialize_position(pos) for pos in p.positions]
    else:
        data["positions"] = []
    return data


@router.post("", response_model=ApiResponse)
async def create_portfolio(
    data: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    portfolio = await portfolio_repo.create_portfolio(db, data, current_user.id)
    return ApiResponse(
        success=True,
        message="Portfolio creado exitosamente",
        data=serialize_portfolio(portfolio),
    )


@router.get("", response_model=ApiResponse)
async def list_portfolios(
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    portfolios, total = await portfolio_repo.list_portfolios(
        db, current_user.id, params.page, params.page_size
    )
    # portfolios tienen positions eager-loaded por selectinload
    items = [serialize_portfolio(p, include_positions=True) for p in portfolios]
    paginated = PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size if total > 0 else 0,
    )
    return ApiResponse(success=True, message="Portfolios listados", data=paginated.model_dump())


@router.get("/{portfolio_id}", response_model=ApiResponse)
async def get_portfolio(
    portfolio_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # get_portfolio usa selectinload → positions eager-loaded
    portfolio = await portfolio_repo.get_portfolio(db, portfolio_id, current_user.id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio no encontrado")
    return ApiResponse(
        success=True,
        message="Portfolio obtenido",
        data=serialize_portfolio(portfolio, include_positions=True),
    )


@router.put("/{portfolio_id}", response_model=ApiResponse)
async def update_portfolio(
    portfolio_id: UUID,
    data: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    portfolio = await portfolio_repo.update_portfolio(db, portfolio_id, current_user.id, data)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio no encontrado")
    return ApiResponse(
        success=True,
        message="Portfolio actualizado",
        data=serialize_portfolio(portfolio),
    )


@router.delete("/{portfolio_id}", response_model=ApiResponse)
async def delete_portfolio(
    portfolio_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await portfolio_repo.delete_portfolio(db, portfolio_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Portfolio no encontrado")
    return ApiResponse(success=True, message="Portfolio eliminado")


# --- Positions ---

@router.post("/{portfolio_id}/positions", response_model=ApiResponse)
async def add_position(
    portfolio_id: UUID,
    data: PositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    position = await position_repo.add_position(db, portfolio_id, current_user.id, data)
    if not position:
        raise HTTPException(status_code=404, detail="Portfolio no encontrado")
    return ApiResponse(
        success=True,
        message="Posición agregada",
        data=serialize_position(position),
    )


@router.put("/{portfolio_id}/positions/{position_id}", response_model=ApiResponse)
async def update_position(
    portfolio_id: UUID,
    position_id: UUID,
    data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    position = await position_repo.update_position(db, position_id, current_user.id, data)
    if not position:
        raise HTTPException(status_code=404, detail="Posición no encontrada")
    return ApiResponse(
        success=True,
        message="Posición actualizada",
        data=serialize_position(position),
    )


@router.delete("/{portfolio_id}/positions/{position_id}", response_model=ApiResponse)
async def remove_position(
    portfolio_id: UUID,
    position_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await position_repo.remove_position(db, position_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Posición no encontrada")
    return ApiResponse(success=True, message="Posición eliminada")
