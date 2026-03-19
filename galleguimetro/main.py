import logging
import os
import uuid
from datetime import datetime, date, timedelta
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import settings
from .models.schemas import ApiResponse, GreeksRequest, OptionData, OptionType
from .services.greeks_calculator import GreeksCalculator
from .services.websocket_manager import ws_manager
from .routers import auth, portfolios, options, strategies, alerts, bridge

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    logger.info("Iniciando Galleguimetro API...")
    yield
    logger.info("Deteniendo Galleguimetro API...")


# Inicializar FastAPI
app = FastAPI(
    title="Galleguimetro API",
    description="Sistema de análisis de opciones financieras en tiempo real",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS - usar orígenes configurados
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers bajo /api
app.include_router(auth.router, prefix="/api")
app.include_router(portfolios.router, prefix="/api")
app.include_router(options.router, prefix="/api")
app.include_router(strategies.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(bridge.router, prefix="/api")

# Servicio de griegas (sin DB, cálculo puro)
greeks_calculator_service = GreeksCalculator()


# --- Endpoints públicos ---

@app.get("/", response_model=ApiResponse)
async def root():
    return ApiResponse(
        success=True,
        message="Galleguimetro API está operativa",
        data={"timestamp": datetime.utcnow().isoformat(), "version": "0.2.0"},
    )


@app.get("/health", response_model=ApiResponse)
async def health_check():
    return ApiResponse(
        success=True,
        message="Servicios operativos",
        data={
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "websocket_connections": ws_manager.connection_count,
        },
    )


# Endpoint público de cálculo de griegas (sin auth para facilitar pruebas)
@app.post("/greeks/calculate", response_model=ApiResponse)
async def calculate_option_greeks(request: GreeksRequest):
    try:
        response = greeks_calculator_service.calculate_greeks(request)
        return ApiResponse(
            success=True,
            message="Griegas calculadas exitosamente",
            data=response.model_dump(),
        )
    except ValueError as ve:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Error de validación: {str(ve)}")
    except RuntimeError as re:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error en cálculo: {str(re)}")


@app.post("/test/greeks", response_model=ApiResponse)
async def test_greeks_calculation():
    """Endpoint de prueba para griegas con datos de ejemplo."""
    future_date = date.today() + timedelta(days=90)
    example_option = OptionData(
        symbol="TEST240920C01500000",
        underlying_symbol="TEST",
        option_type=OptionType.CALL,
        strike_price=150.0,
        expiration_date=future_date,
        implied_volatility=0.20,
        dividend_yield=0.01,
        risk_free_rate=0.03,
    )
    example_request = GreeksRequest(
        option_data=example_option,
        spot_price=155.0,
        risk_free_rate=0.03,
        dividend_yield=0.01,
        time_to_expiration_years=0.25,
    )
    response = greeks_calculator_service.calculate_greeks(example_request)
    return ApiResponse(
        success=True,
        message="Griegas de prueba calculadas",
        data=response.model_dump(),
    )


# --- WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "subscribe":
                channel = data.get("channel", data.get("event"))
                if channel:
                    ws_manager.subscribe(client_id, channel)
                    await ws_manager.send_personal(client_id, {
                        "type": "subscribed",
                        "channel": channel,
                    })
            elif msg_type == "unsubscribe":
                channel = data.get("channel", data.get("event"))
                if channel:
                    ws_manager.unsubscribe(client_id, channel)
            elif msg_type == "ping":
                await ws_manager.send_personal(client_id, {"type": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Error en WebSocket {client_id}: {e}")
        ws_manager.disconnect(client_id)


# --- Ejecución ---
if __name__ == "__main__":
    logger.info(f"Iniciando servidor en http://{settings.host}:{settings.port}")
    logger.info(f"Docs: http://{settings.host}:{settings.port}/docs")

    uvicorn.run(
        "galleguimetro.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
