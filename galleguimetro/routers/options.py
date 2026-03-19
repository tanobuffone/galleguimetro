from uuid import UUID
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import get_db
from ..models.database import User, Option
from ..models.schemas import (
    ApiResponse, PaginationParams, PaginatedResponse,
    OptionCreate, OptionUpdate,
    GreeksRequest,
)
from ..services.auth import get_current_user
from ..services.greeks_calculator import GreeksCalculator
from ..repositories import option_repo

router = APIRouter(prefix="/options", tags=["options"])

greeks_calculator = GreeksCalculator()


def serialize_option(o: Option) -> Dict[str, Any]:
    return {
        "id": str(o.id),
        "symbol": o.symbol,
        "underlying_id": str(o.underlying_id),
        "option_type": o.option_type.value if hasattr(o.option_type, 'value') else str(o.option_type),
        "strike_price": o.strike_price,
        "expiration_date": o.expiration_date.isoformat() if o.expiration_date else None,
        "implied_volatility": o.implied_volatility,
        "dividend_yield": o.dividend_yield or 0.0,
        "risk_free_rate": o.risk_free_rate or 0.0,
        "last_price": o.last_price,
        "bid": o.bid,
        "ask": o.ask,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
    }


@router.post("", response_model=ApiResponse)
async def create_option(
    data: OptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    option = await option_repo.create_option(db, data)
    return ApiResponse(success=True, message="Opción creada", data=serialize_option(option))


@router.get("", response_model=ApiResponse)
async def list_options(
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    options, total = await option_repo.list_options(db, params.page, params.page_size)
    items = [serialize_option(o) for o in options]
    paginated = PaginatedResponse(
        items=items, total=total, page=params.page, page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size if total > 0 else 0,
    )
    return ApiResponse(success=True, message="Opciones listadas", data=paginated.model_dump())


@router.get("/chain/{symbol}", response_model=ApiResponse)
async def get_option_chain(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    options = await option_repo.get_option_chain(db, symbol)
    items = [serialize_option(o) for o in options]
    return ApiResponse(success=True, message=f"Cadena de opciones para {symbol}", data=items)


@router.get("/{option_id}", response_model=ApiResponse)
async def get_option(
    option_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    option = await option_repo.get_option(db, option_id)
    if not option:
        raise HTTPException(status_code=404, detail="Opción no encontrada")
    return ApiResponse(success=True, message="Opción obtenida", data=serialize_option(option))


@router.put("/{option_id}", response_model=ApiResponse)
async def update_option(
    option_id: UUID,
    data: OptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    option = await option_repo.update_option(db, option_id, data)
    if not option:
        raise HTTPException(status_code=404, detail="Opción no encontrada")
    return ApiResponse(success=True, message="Opción actualizada", data=serialize_option(option))


@router.delete("/{option_id}", response_model=ApiResponse)
async def delete_option(
    option_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await option_repo.delete_option(db, option_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Opción no encontrada")
    return ApiResponse(success=True, message="Opción eliminada")


@router.post("/calculate-greeks", response_model=ApiResponse)
async def calculate_greeks(
    request: GreeksRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        response = greeks_calculator.calculate_greeks(request)
        return ApiResponse(success=True, message="Griegas calculadas", data=response.model_dump())
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=f"Error en cálculo: {str(re)}")
