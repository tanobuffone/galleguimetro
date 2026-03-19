from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime, date
from typing import Optional, List, Union, Dict, Any
from enum import Enum
from uuid import UUID


# --- Enumeraciones ---

class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

class PositionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class StrategyType(str, Enum):
    SINGLE = "single"
    SPREAD = "spread"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"
    COLLAR = "collar"


# --- Modelos base de datos ---

class UnderlyingPrice(BaseModel):
    symbol: str = Field(..., description="Símbolo del activo subyacente")
    price: float = Field(..., gt=0, description="Precio actual del subyacente")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OptionData(BaseModel):
    symbol: str = Field(..., description="Símbolo de la opción")
    underlying_symbol: str = Field(..., description="Símbolo del activo subyacente")
    option_type: OptionType = Field(..., description="Tipo de opción")
    strike_price: float = Field(..., gt=0, description="Precio de strike")
    expiration_date: date = Field(..., description="Fecha de vencimiento")
    implied_volatility: Optional[float] = Field(None, ge=0)
    dividend_yield: Optional[float] = Field(None, ge=0)
    risk_free_rate: Optional[float] = Field(None, ge=0)
    last_price: Optional[float] = Field(None, ge=0)
    bid: Optional[float] = Field(None, ge=0)
    ask: Optional[float] = Field(None, gt=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('expiration_date')
    @classmethod
    def validate_expiration(cls, v: date) -> date:
        if v <= date.today():
            raise ValueError("La fecha de vencimiento debe ser en el futuro")
        return v


class Greeks(BaseModel):
    delta: Optional[float] = None
    gamma: Optional[float] = Field(None, ge=0)
    theta: Optional[float] = None
    vega: Optional[float] = Field(None, ge=0)
    rho: Optional[float] = None
    epsilon: Optional[float] = Field(None, ge=0)


class OptionPosition(BaseModel):
    option_symbol: str = Field(...)
    quantity: int = Field(...)
    entry_price: Optional[float] = Field(None, ge=0)
    current_price: Optional[float] = Field(None, ge=0)
    market_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: Optional[float] = None
    status: PositionStatus = Field(default=PositionStatus.OPEN)
    entry_date: datetime = Field(default_factory=datetime.utcnow)
    exit_date: Optional[datetime] = None
    fees: Optional[float] = Field(default=0.0, ge=0)


class OptionsPortfolio(BaseModel):
    portfolio_id: Optional[str] = None
    name: str = Field(...)
    description: Optional[str] = None
    owner: Optional[str] = None
    positions: List[OptionPosition] = Field(default_factory=list)
    total_market_value: Optional[float] = Field(None, ge=0)
    total_unrealized_pnl: Optional[float] = None
    total_realized_pnl: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('positions', mode='before')
    @classmethod
    def validate_positions(cls, v: Any) -> Any:
        if not isinstance(v, list):
            raise ValueError("Las posiciones deben ser una lista")
        return v


class OptionsStrategy(BaseModel):
    strategy_id: Optional[str] = None
    strategy_type: StrategyType = Field(...)
    name: str = Field(...)
    description: Optional[str] = None
    underlying_symbol: str = Field(...)
    legs: List[Dict[str, Any]] = Field(...)
    net_debit_credit: Optional[float] = None
    max_profit: Optional[float] = None
    max_loss: Optional[float] = None
    breakeven_points: Optional[List[float]] = None
    risk_reward_ratio: Optional[float] = None
    status: PositionStatus = Field(default=PositionStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# --- Schemas de Request/Response para Greeks ---

class GreeksRequest(BaseModel):
    option_data: OptionData = Field(...)
    spot_price: float = Field(..., gt=0)
    risk_free_rate: float = Field(..., ge=0)
    dividend_yield: float = Field(default=0.0, ge=0)
    time_to_expiration_years: float = Field(..., gt=0)


class GreeksResponse(BaseModel):
    option_symbol: str = Field(...)
    greeks: Greeks = Field(...)
    input_parameters: Dict[str, Any] = Field(...)
    calculation_timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Schemas de Market Data ---

class MarketData(BaseModel):
    symbol: str = Field(...)
    price: float = Field(..., gt=0)
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = Field(None, ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# --- Schemas de Alertas ---

class Alert(BaseModel):
    alert_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    message: str = Field(...)
    condition_met: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    triggered_at: Optional[datetime] = None


# --- Schemas de API Response ---

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# --- Schemas CRUD para Portfolio (faltantes) ---

class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    initial_value: Optional[float] = Field(default=0.0, ge=0)


class PortfolioUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class PortfolioResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    owner_id: Optional[UUID] = None
    total_market_value: float = 0.0
    total_unrealized_pnl: float = 0.0
    total_realized_pnl: float = 0.0
    created_at: datetime
    updated_at: datetime
    positions: List[Any] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# --- Schemas CRUD para Position ---

class PositionCreate(BaseModel):
    option_id: UUID
    quantity: int = Field(..., description="Positivo para largo, negativo para corto")
    entry_price: Optional[float] = Field(None, ge=0)
    current_price: Optional[float] = Field(None, ge=0)
    fees: Optional[float] = Field(default=0.0, ge=0)


class PositionUpdate(BaseModel):
    quantity: Optional[int] = None
    current_price: Optional[float] = Field(None, ge=0)
    status: Optional[PositionStatus] = None
    fees: Optional[float] = Field(None, ge=0)


class PositionResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    option_id: UUID
    quantity: int
    entry_price: Optional[float] = None
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: float = 0.0
    status: str
    entry_date: datetime
    exit_date: Optional[datetime] = None
    fees: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Schemas CRUD para Option ---

class OptionCreate(BaseModel):
    symbol: str = Field(..., min_length=1)
    underlying_symbol: str = Field(..., min_length=1)
    option_type: OptionType
    strike_price: float = Field(..., gt=0)
    expiration_date: date
    implied_volatility: Optional[float] = Field(None, ge=0)
    dividend_yield: Optional[float] = Field(default=0.0, ge=0)
    risk_free_rate: Optional[float] = Field(default=0.0, ge=0)
    last_price: Optional[float] = Field(None, ge=0)
    bid: Optional[float] = Field(None, ge=0)
    ask: Optional[float] = Field(None, gt=0)


class OptionUpdate(BaseModel):
    implied_volatility: Optional[float] = Field(None, ge=0)
    last_price: Optional[float] = Field(None, ge=0)
    bid: Optional[float] = Field(None, ge=0)
    ask: Optional[float] = Field(None, gt=0)
    dividend_yield: Optional[float] = Field(None, ge=0)
    risk_free_rate: Optional[float] = Field(None, ge=0)


class OptionResponse(BaseModel):
    id: UUID
    symbol: str
    underlying_id: UUID
    option_type: str
    strike_price: float
    expiration_date: datetime
    implied_volatility: Optional[float] = None
    dividend_yield: float = 0.0
    risk_free_rate: float = 0.0
    last_price: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Schemas CRUD para Strategy ---

class StrategyLegCreate(BaseModel):
    option_id: UUID
    quantity: int
    action: str = Field(..., pattern="^(buy|sell)$")


class StrategyCreate(BaseModel):
    strategy_type: StrategyType
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    underlying_symbol: str = Field(..., min_length=1)
    portfolio_id: Optional[UUID] = None
    legs: List[StrategyLegCreate] = Field(..., min_length=1)


class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[PositionStatus] = None


class StrategyResponse(BaseModel):
    id: UUID
    strategy_type: str
    name: str
    description: Optional[str] = None
    portfolio_id: Optional[UUID] = None
    underlying_id: UUID
    net_debit_credit: Optional[float] = None
    max_profit: Optional[float] = None
    max_loss: Optional[float] = None
    breakeven_points: Optional[List[float]] = None
    risk_reward_ratio: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime
    legs: List[Any] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# --- Schemas CRUD para Alert ---

class AlertCreate(BaseModel):
    portfolio_id: Optional[UUID] = None
    strategy_id: Optional[UUID] = None
    message: str = Field(..., min_length=1)
    condition: Optional[str] = None


class AlertUpdate(BaseModel):
    message: Optional[str] = None
    condition_met: Optional[bool] = None


class AlertResponse(BaseModel):
    id: UUID
    portfolio_id: Optional[UUID] = None
    strategy_id: Optional[UUID] = None
    message: str
    condition_met: bool
    triggered_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Schemas para Auth ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
