<p align="center">
  <h1 align="center">Galleguimetro</h1>
  <p align="center">
    Sistema de análisis de opciones financieras en tiempo real
    <br />
    <em>Reemplazá Excel + etrader con una plataforma web profesional para opciones</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0--alpha-blue" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.11%2B-green" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="License" />
  <img src="https://img.shields.io/badge/fastapi-0.104%2B-009688" alt="FastAPI" />
  <img src="https://img.shields.io/badge/react-18.2%2B-61dafb" alt="React" />
  <img src="https://img.shields.io/badge/quantlib-1.26%2B-orange" alt="QuantLib" />
</p>

---

## Qué es Galleguimetro

Galleguimetro es una plataforma de análisis de opciones financieras que conecta datos de mercado en tiempo real (vía DDE desde Excel/etrader) con un motor de cálculo de griegas basado en **QuantLib** y una interfaz web moderna en **React + TypeScript**.

Diseñado para operadores que trabajan con opciones en el mercado argentino (BYMA), reemplaza el flujo manual de planillas Excel con:

- **Cálculo automático de griegas** (delta, gamma, theta, vega, rho) usando Black-Scholes-Merton
- **Análisis de estrategias** (spreads, straddles, strangles, butterflies, collars)
- **Gestión de portfolios** con tracking de P&L en tiempo real
- **Actualización en tiempo real** vía WebSocket desde el bridge DDE
- **Diagramas de payoff** y charts profesionales con TradingView

## Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                    Windows Host                               │
│  ┌─────────┐    ┌─────────┐    ┌──────────────────────┐     │
│  │ etrader │───▶│  Excel   │───▶│  DDE Bridge (Python) │     │
│  └─────────┘DDE └─────────┘    └──────────┬───────────┘     │
│                                            │ HTTP POST       │
│  ┌─────────────────────────────────────────┼─────────────┐  │
│  │               WSL2 / Docker             │             │  │
│  │                                         ▼             │  │
│  │  ┌──────────┐   ┌──────────────────────────────┐     │  │
│  │  │PostgreSQL│◀─▶│   FastAPI Backend (Python)    │     │  │
│  │  │   16     │   │  + QuantLib + WebSocket       │     │  │
│  │  └──────────┘   └──────────────┬───────────────┘     │  │
│  │  ┌──────────┐                  │ REST + WS           │  │
│  │  │  Qdrant  │                  ▼                     │  │
│  │  │ (vector) │   ┌──────────────────────────────┐     │  │
│  │  └──────────┘   │  React Frontend (TypeScript) │     │  │
│  │                 │  + Redux + TradingView        │     │  │
│  │                 └──────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Stack Tecnológico

| Capa | Tecnologías |
|------|-------------|
| **Backend** | Python 3.11+, FastAPI, QuantLib, SQLAlchemy 2.0 (async), Pydantic v2 |
| **Frontend** | React 18, TypeScript, Redux Toolkit, Recharts, TradingView Widget |
| **Base de Datos** | PostgreSQL 16 (asyncpg), Qdrant (vector search) |
| **Bridge DDE** | Python + pywin32 (COM automation), polling configurable |
| **Infra** | Docker, Docker Compose, Nginx, GitHub Actions CI/CD |
| **Auth** | JWT (HS256) + bcrypt |

## Funcionalidades

### Motor de Opciones
- Pricing con Black-Scholes-Merton vía QuantLib
- Cálculo de griegas: delta, gamma, theta, vega, rho, epsilon
- Cadena de opciones por subyacente y vencimiento
- Validación automática de fechas de expiración

### Estrategias
- Single leg, spread, straddle, strangle, butterfly, collar
- Análisis de riesgo/recompensa por estrategia
- Diagrama de payoff interactivo

### Portfolio
- Múltiples portfolios por usuario
- Tracking de posiciones (cantidad, precio entrada, P&L)
- Valuación en tiempo real con datos del bridge
- Métricas agregadas: market value, unrealized/realized P&L

### Datos en Tiempo Real
- Bridge DDE que lee Excel vía COM automation (Windows nativo)
- Polling configurable (default 5s)
- WebSocket broadcast a todos los clientes conectados
- Modo dry-run para testing sin enviar datos

### Alertas
- Alertas configurables por condición de precio
- Monitoreo continuo sobre datos en tiempo real

## Inicio Rápido

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- (Opcional) Windows con etrader + Excel para el bridge DDE

### 1. Clonar y configurar

```bash
git clone https://github.com/<tu-usuario>/galleguimetro.git
cd galleguimetro
cp .env.example .env
# Editar .env con tus valores (SECRET_KEY, DATABASE_URL, etc.)
```

### 2. Levantar servicios con Docker

```bash
make docker-up
# Levanta PostgreSQL + Qdrant
```

### 3. Backend

```bash
make install        # Instala dependencias Python + Node
make migrate        # Corre migraciones Alembic
make dev            # Inicia FastAPI en localhost:8000
```

### 4. Frontend

```bash
make dev-frontend   # Inicia React en localhost:3000
```

### 5. Bridge DDE (Windows, opcional)

```bash
cd bridge/
pip install pywin32 requests websocket-client
python dde_bridge.py --backend-url http://localhost:8000 \
                     --username admin --password admin12345 \
                     --interval 5
```

### Verificación

```bash
curl http://localhost:8000/health          # Health check
curl -X POST http://localhost:8000/test/greeks \
  -H "Content-Type: application/json" \
  -d '{"spot": 100, "strike": 105, "rate": 0.05, "volatility": 0.2, "expiration": "2026-12-31", "option_type": "call"}'
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Registro de usuario |
| `POST` | `/api/auth/login` | Login (devuelve JWT) |
| `GET` | `/api/options` | Listar opciones |
| `GET` | `/api/options/chain/{symbol}` | Cadena de opciones |
| `POST` | `/greeks/calculate` | Calcular griegas |
| `GET` | `/api/portfolios` | Listar portfolios |
| `POST` | `/api/portfolios` | Crear portfolio |
| `GET` | `/api/strategies` | Listar estrategias |
| `POST` | `/api/bridge/market-data` | Recibir datos del bridge |
| `WS` | `/ws` | WebSocket tiempo real |

> Ver documentación completa de la API en `http://localhost:8000/docs` (Swagger UI)

## Comandos de Desarrollo

```bash
make install           # Instalar todas las dependencias
make dev               # Servidor backend (uvicorn --reload)
make dev-frontend      # Servidor frontend (vite)
make test              # Todos los tests
make test-unit         # Tests unitarios
make test-integration  # Tests de integración
make lint              # Linting (ruff)
make format            # Auto-format (ruff)
make type-check        # Type checking (mypy)
make migrate           # Migraciones de BD
make docker-up         # Levantar Docker services
make docker-down       # Bajar Docker services
make docker-prod       # Build y run producción
```

## Estructura del Proyecto

```
galleguimetro/
├── galleguimetro/           # Backend Python (FastAPI)
│   ├── main.py              # Entry point + WebSocket
│   ├── config/              # Settings + database config
│   ├── models/              # ORM models + Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Lógica de negocio (griegas, auth, WS)
│   └── repositories/        # Data access layer
├── frontend/                # Frontend React + TypeScript
│   ├── src/
│   │   ├── components/      # Componentes UI (options, portfolio, charts)
│   │   ├── pages/           # Páginas
│   │   ├── services/        # Clientes API + WebSocket
│   │   ├── store/           # Redux slices
│   │   └── types/           # TypeScript interfaces
│   └── Dockerfile           # Build multi-stage (Node + Nginx)
├── bridge/                  # Bridge DDE (Windows nativo)
│   ├── dde_bridge.py        # Servicio principal
│   └── bridge_config.json   # Mapeo de columnas Excel
├── alembic/                 # Migraciones de base de datos
├── tests/                   # Unit + integration tests
├── scripts/                 # Scripts de setup
├── .github/workflows/       # CI/CD (GitHub Actions)
├── docker-compose.yml       # Entorno desarrollo
├── docker-compose.prod.yml  # Entorno producción
├── Dockerfile               # Backend multi-stage
├── Makefile                 # Comandos de desarrollo
└── DEPLOY.md                # Guía completa de deploy
```

## Deploy a Producción

```bash
make docker-prod
# O manualmente:
docker compose -f docker-compose.prod.yml up --build -d
```

Ver [DEPLOY.md](DEPLOY.md) para la guía completa paso a paso.

## CI/CD

El pipeline de GitHub Actions ejecuta en cada push a `main`/`develop`:

1. **Lint & Type Check** - ruff + mypy
2. **Backend Tests** - pytest (unit + integration)
3. **Frontend Build** - npm build
4. **Docker Build** - Imágenes de producción (solo en `main`)

## Roadmap

- [x] Backend FastAPI con async PostgreSQL
- [x] Motor de griegas con QuantLib
- [x] Frontend React con Redux
- [x] Bridge DDE para Excel/etrader
- [x] Autenticación JWT
- [x] WebSocket en tiempo real
- [x] Docker + Docker Compose
- [x] CI/CD con GitHub Actions
- [ ] Análisis completo de estrategias multi-leg
- [ ] Búsqueda semántica con Qdrant
- [ ] Alertas avanzadas con notificaciones push
- [ ] Deploy cloud (VPS/Railway)
- [ ] App móvil (PWA)

## Licencia

[MIT](LICENSE)
