from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from enum import Enum

# Importar la Base desde la configuración de la BD
from ..config.database import Base

# Reutilizar las enumeraciones de schemas.py para consistencia
# O definirlas aquí si se prefiere mantener la capa de BD separada de la de Pydantic.
# Para este ejemplo, las importaremos o redefiniremos si hay problemas de circularidad.
# Dado que database.py no depende directamente de schemas.py (solo main.py y services.py lo hacen),
# podemos redefinir las enumeraciones aquí para evitar dependencias circulares en la definición de modelos.

# Enumeración para tipos de opciones
class OptionTypeDB(str, Enum):
    CALL = "call"
    PUT = "put"

# Enumeración para estado de la posición
class PositionStatusDB(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

# Enumeración para estrategia
class StrategyTypeDB(str, Enum):
    SINGLE = "single"
    SPREAD = "spread"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"
    COLLAR = "collar"

# Modelo para la tabla de usuarios (futura implementación de autenticación)
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) # Nunca almacenar contraseñas en texto plano
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    portfolios = relationship("Portfolio", back_populates="owner")
    # Otras relaciones según sea necesario

# Modelo para la tabla de activos subyacentes
class Underlying(Base):
    __tablename__ = "underlyings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String, unique=True, index=True, nullable=False) # Ej: AAPL, MSFT
    name = Column(String, nullable=True) # Ej: Apple Inc.
    asset_type = Column(String, default="stock") # stock, index, futures, etc.
    exchange = Column(String, nullable=True) # Ej: NASDAQ, NYSE
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    options = relationship("Option", back_populates="underlying")
    strategies = relationship("Strategy", back_populates="underlying")

# Modelo para la tabla de opciones
class Option(Base):
    __tablename__ = "options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String, unique=True, index=True, nullable=False) # Símbolo de la opción (e.g., AAPL240315C00200000)
    underlying_id = Column(UUID(as_uuid=True), ForeignKey("underlyings.id"), nullable=False)
    option_type = Column(SQLEnum(OptionTypeDB), nullable=False)
    strike_price = Column(Float, nullable=False)
    expiration_date = Column(DateTime, nullable=False) # Almacenar como DateTime para facilitar consultas
    implied_volatility = Column(Float, nullable=True) # Volatilidad implícita actual
    dividend_yield = Column(Float, default=0.0) # Rendimiento del dividendo
    risk_free_rate = Column(Float, default=0.0) # Tasa libre de riesgo (puede ser de un term structure)
    # Precio de la opción (puede venir de DDE o ser calculado)
    last_price = Column(Float, nullable=True)
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Metadata adicional (ej. fuente del precio, liquidez, etc.)
    extra_metadata = Column(JSON, nullable=True)

    # Relaciones
    underlying = relationship("Underlying", back_populates="options")
    option_positions = relationship("OptionPosition", back_populates="option")
    strategy_legs = relationship("StrategyLeg", back_populates="option")

# Modelo para la tabla de portfolios
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # Puede ser None si no hay usuarios aún
    # Agregados calculados (se pueden calcular en la aplicación o con triggers en BD)
    total_market_value = Column(Float, default=0.0)
    total_unrealized_pnl = Column(Float, default=0.0)
    total_realized_pnl = Column(Float, default=0.0)
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    owner = relationship("User", back_populates="portfolios")
    positions = relationship("OptionPosition", back_populates="portfolio", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="portfolio", cascade="all, delete-orphan")

# Modelo para la tabla de posiciones de opciones
class OptionPosition(Base):
    __tablename__ = "option_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id"), nullable=False)
    quantity = Column(Integer, nullable=False) # Cantidad de contratos (positivo para largo, negativo para corto)
    entry_price = Column(Float, nullable=True) # Precio de entrada promedio
    current_price = Column(Float, nullable=True) # Precio actual de la opción (se puede actualizar periódicamente)
    market_value = Column(Float, nullable=True) # Valor de mercado de la posición (quantity * current_price)
    unrealized_pnl = Column(Float, nullable=True) # PNL no realizado
    realized_pnl = Column(Float, default=0.0) # PNL realizado
    status = Column(SQLEnum(PositionStatusDB), default=PositionStatusDB.OPEN)
    entry_date = Column(DateTime, default=datetime.utcnow)
    exit_date = Column(DateTime, nullable=True)
    fees = Column(Float, default=0.0)
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    portfolio = relationship("Portfolio", back_populates="positions")
    option = relationship("Option", back_populates="option_positions")

# Modelo para la tabla de estrategias
class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=True) # Puede ser None si es una estrategia global
    strategy_type = Column(SQLEnum(StrategyTypeDB), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    underlying_id = Column(UUID(as_uuid=True), ForeignKey("underlyings.id"), nullable=False)
    # Agregados calculados
    net_debit_credit = Column(Float, nullable=True) # Costo neto de la estrategia (debito o crédito)
    max_profit = Column(Float, nullable=True)
    max_loss = Column(Float, nullable=True)
    breakeven_points = Column(JSON, nullable=True) # Array de puntos de equilibrio
    risk_reward_ratio = Column(Float, nullable=True)
    status = Column(SQLEnum(PositionStatusDB), default=PositionStatusDB.OPEN)
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    portfolio = relationship("Portfolio", back_populates="strategies")
    underlying = relationship("Underlying", back_populates="strategies")
    legs = relationship("StrategyLeg", back_populates="strategy", cascade="all, delete-orphan")

# Modelo para la tabla de piernas (legs) de una estrategia
class StrategyLeg(Base):
    __tablename__ = "strategy_legs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id"), nullable=False)
    quantity = Column(Integer, nullable=False) # Cantidad de contratos para esta pierna
    action = Column(String, nullable=False) # "buy" o "sell"
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    strategy = relationship("Strategy", back_populates="legs")
    option = relationship("Option", back_populates="strategy_legs")

# Modelo para la tabla de alertas
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=True)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=True)
    message = Column(Text, nullable=False)
    condition_met = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    portfolio = relationship("Portfolio")
    strategy = relationship("Strategy")

# Modelo para la tabla de logs de mercado (opcional, para datos históricos)
class MarketDataLog(Base):
    __tablename__ = "market_data_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    underlying_id = Column(UUID(as_uuid=True), ForeignKey("underlyings.id"), nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    # Timestamps
    logged_at = Column(DateTime, default=datetime.utcnow, index=True) # Indexado para consultas rápidas

    # Relaciones
    underlying = relationship("Underlying")

# Modelo para la tabla de logs de cálculo de griegas (opcional, para auditoría)
class GreeksCalculationLog(Base):
    __tablename__ = "greeks_calculation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id"), nullable=False)
    spot_price = Column(Float, nullable=False)
    risk_free_rate = Column(Float, nullable=False)
    dividend_yield = Column(Float, nullable=False)
    time_to_expiration_years = Column(Float, nullable=False)
    calculated_greeks = Column(JSON, nullable=False) # Almacenar delta, gamma, theta, vega, rho como JSON
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relaciones
    option = relationship("Option")

# Nota: Se pueden añadir más modelos según las necesidades del proyecto,
# por ejemplo, para transacciones, comisiones, configuraciones, etc.