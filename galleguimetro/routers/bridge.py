"""
Router para recibir datos del DDE Bridge (Windows).
Recibe market data desde el bridge y los persiste/broadcastea.
"""
import logging
from typing import Any, Dict, List
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config.database import get_db
from ..models.database import User, Option, Underlying, MarketDataLog
from ..models.schemas import ApiResponse
from ..services.auth import get_current_user
from ..services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bridge", tags=["bridge"])


def parse_date(val: Any) -> datetime:
    """Convierte string/date/datetime a datetime para PostgreSQL."""
    if val is None:
        return datetime.utcnow()
    if isinstance(val, datetime):
        return val
    if isinstance(val, date):
        return datetime(val.year, val.month, val.day)
    if isinstance(val, str):
        # Intentar varios formatos
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S%z"):
            try:
                return datetime.strptime(val.split("+")[0].split("T")[0], "%Y-%m-%d")
            except ValueError:
                continue
        logger.warning(f"No se pudo parsear fecha: {val}")
        return datetime.utcnow()
    return datetime.utcnow()


def normalize_option_type(val: Any) -> str:
    """Normaliza tipo de opción a formato del enum DB."""
    if val is None:
        return "call"
    s = str(val).strip().lower()
    if s in ("c", "call", "compra"):
        return "call"
    if s in ("p", "put", "v", "venta"):
        return "put"
    return "call"


@router.post("/market-data", response_model=ApiResponse)
async def receive_market_data(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recibe datos de mercado del DDE Bridge en Windows."""
    options_data = payload.get("options", [])
    if not options_data:
        return ApiResponse(success=True, message="Sin datos para procesar")

    logger.info(f"Bridge: recibiendo {len(options_data)} opciones")
    updated_count = 0
    created_count = 0
    errors = []

    for opt in options_data:
        try:
            symbol = opt.get("symbol")
            if not symbol:
                continue

            # Buscar opción existente
            result = await db.execute(select(Option).where(Option.symbol == symbol))
            existing = result.scalar_one_or_none()

            if existing:
                # Actualizar precios
                if opt.get("last_price") is not None:
                    existing.last_price = float(opt["last_price"])
                if opt.get("bid") is not None:
                    existing.bid = float(opt["bid"])
                if opt.get("ask") is not None:
                    existing.ask = float(opt["ask"])
                if opt.get("implied_volatility") is not None:
                    existing.implied_volatility = float(opt["implied_volatility"])
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Asegurar underlying existe
                underlying_symbol = opt.get("underlying_symbol", symbol[:4])
                u_result = await db.execute(
                    select(Underlying).where(Underlying.symbol == underlying_symbol)
                )
                underlying = u_result.scalar_one_or_none()
                if not underlying:
                    underlying = Underlying(symbol=underlying_symbol, name=underlying_symbol)
                    db.add(underlying)
                    await db.flush()

                new_option = Option(
                    symbol=symbol,
                    underlying_id=underlying.id,
                    option_type=normalize_option_type(opt.get("option_type")),
                    strike_price=float(opt.get("strike_price", 0)),
                    expiration_date=parse_date(opt.get("expiration_date")),
                    last_price=float(opt["last_price"]) if opt.get("last_price") else None,
                    bid=float(opt["bid"]) if opt.get("bid") else None,
                    ask=float(opt["ask"]) if opt.get("ask") else None,
                    implied_volatility=float(opt["implied_volatility"]) if opt.get("implied_volatility") else None,
                    dividend_yield=0.0,
                    risk_free_rate=0.0,
                )
                db.add(new_option)
                created_count += 1

        except Exception as e:
            errors.append(f"{opt.get('symbol', '?')}: {str(e)[:100]}")
            logger.error(f"Error procesando opción {opt.get('symbol')}: {e}")
            # Rollback parcial para continuar con las siguientes
            await db.rollback()
            # Re-abrir transacción
            break  # Si hay error de sesión, mejor parar y reportar

    try:
        await db.flush()
    except Exception as e:
        logger.error(f"Error en flush final: {e}")
        errors.append(f"flush: {str(e)[:100]}")

    # Broadcast a WebSocket
    await ws_manager.broadcast("market_data", {
        "updated": updated_count,
        "created": created_count,
        "timestamp": datetime.utcnow().isoformat(),
    })

    result_msg = f"Procesadas: {updated_count} actualizadas, {created_count} creadas"
    if errors:
        result_msg += f", {len(errors)} errores"

    logger.info(result_msg)

    return ApiResponse(
        success=True,
        message=result_msg,
        data={"updated": updated_count, "created": created_count, "errors": errors[:5]},
    )


@router.post("/portfolio-sync", response_model=ApiResponse)
async def receive_portfolio_sync(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recibe posiciones del portfolio desde el DDE Bridge."""
    positions = payload.get("positions", [])
    await ws_manager.broadcast("portfolio_update", {
        "positions": positions,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return ApiResponse(
        success=True,
        message=f"Sincronizadas {len(positions)} posiciones",
        data={"count": len(positions)},
    )


@router.get("/status", response_model=ApiResponse)
async def bridge_status():
    return ApiResponse(
        success=True,
        message="Bridge status",
        data={
            "websocket_connections": ws_manager.connection_count,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
