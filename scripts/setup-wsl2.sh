#!/bin/bash
# ==============================================================
# Galleguimetro - Script de primer deploy en WSL2 Ubuntu Noble
# ==============================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e "  ${RED}✗${NC} $1"; }
log_info() { echo -e "  $1"; }

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "  Galleguimetro - Setup WSL2"
echo "=========================================="
echo "  Directorio: $PROJECT_DIR"
echo ""

# ---- 1. Verificar requisitos ----
echo "[1/7] Verificando requisitos..."

# Python 3.11+
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3; do
    if command -v $cmd &>/dev/null; then
        PY_VER=$($cmd --version 2>&1 | grep -oP '\d+\.\d+')
        PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    log_err "Se necesita Python 3.11+. Instalar con:"
    echo "    sudo apt update && sudo apt install -y python3.12 python3.12-venv python3.12-dev"
    exit 1
fi
log_ok "Python $($PYTHON_CMD --version 2>&1) ($PYTHON_CMD)"

# Docker
if ! command -v docker &>/dev/null; then
    log_err "Docker no instalado."
    exit 1
fi
if ! docker info &>/dev/null 2>&1; then
    log_err "Docker daemon no está corriendo. Iniciar con: sudo service docker start"
    exit 1
fi
log_ok "Docker $(docker --version | grep -oP '\d+\.\d+\.\d+')"

# Node.js
if command -v node &>/dev/null; then
    log_ok "Node $(node --version)"
else
    log_warn "Node.js no instalado. Frontend no se podrá ejecutar."
fi

# uv
if ! command -v uv &>/dev/null; then
    log_info "Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
fi
if command -v uv &>/dev/null; then
    log_ok "uv $(uv --version 2>/dev/null | head -1)"
else
    log_warn "uv no se pudo instalar. Se usará pip."
fi

# ---- 2. Crear .env ----
echo ""
echo "[2/7] Configurando variables de entorno..."

if [ ! -f .env ]; then
    cp .env.example .env
    SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/CAMBIAR-EN-PRODUCCION-usar-openssl-rand-hex-32/$SECRET_KEY/" .env
    log_ok ".env creado con SECRET_KEY generado"
else
    log_ok ".env ya existe"
fi

# Mostrar DATABASE_URL para debug
DB_URL=$(grep "^DATABASE_URL=" .env | cut -d= -f2-)
log_info "DATABASE_URL=$DB_URL"

# ---- 3. Iniciar Docker ----
echo ""
echo "[3/7] Iniciando PostgreSQL y Qdrant..."

# Verificar si hay volúmenes corruptos
POSTGRES_STATUS=$(docker compose ps ws-postgres --format "{{.Status}}" 2>/dev/null || echo "not found")
if echo "$POSTGRES_STATUS" | grep -qi "exited"; then
    log_warn "Contenedor postgres en estado Exited. Revisando logs..."
    docker compose logs ws-postgres 2>/dev/null | tail -5

    # Verificar si es error de initdb (volumen corrupto)
    if docker compose logs ws-postgres 2>/dev/null | grep -q "initdb: error"; then
        log_warn "Volumen de PostgreSQL corrupto. Recreando..."
        docker compose down -v 2>/dev/null
        log_ok "Volúmenes eliminados"
    fi
fi

docker compose up -d 2>&1 | grep -v "^time=" || true
log_info "Esperando que PostgreSQL esté healthy..."

# Esperar con feedback
for i in $(seq 1 60); do
    STATUS=$(docker compose ps ws-postgres --format "{{.Status}}" 2>/dev/null || echo "")
    if echo "$STATUS" | grep -qi "healthy"; then
        log_ok "PostgreSQL listo (${i}s)"
        break
    fi
    if echo "$STATUS" | grep -qi "exited"; then
        log_err "PostgreSQL falló al iniciar. Logs:"
        docker compose logs ws-postgres 2>/dev/null | tail -10
        echo ""
        echo "  Intenta: docker compose down -v && docker compose up -d"
        exit 1
    fi
    if [ "$i" -eq 60 ]; then
        log_err "PostgreSQL no arrancó en 60 segundos."
        echo "  Status: $STATUS"
        echo "  Logs:"
        docker compose logs ws-postgres 2>/dev/null | tail -10
        exit 1
    fi
    printf "."
    sleep 1
done

# Verificar Qdrant
if curl -s http://localhost:7333/health >/dev/null 2>&1; then
    log_ok "Qdrant listo en http://localhost:7333"
else
    log_warn "Qdrant no responde en :7333 (puede estar arrancando)"
fi

# Verificar conexión directa a la DB
if docker exec galleguimetro-postgres psql -U galleguimetro_user -d galleguimetro -c "SELECT 1" &>/dev/null; then
    log_ok "Conexión directa a PostgreSQL OK"
else
    log_err "No se puede conectar a PostgreSQL dentro del contenedor"
    docker compose logs ws-postgres 2>/dev/null | tail -10
    exit 1
fi

# ---- 4. Instalar dependencias Python ----
echo ""
echo "[4/7] Instalando dependencias Python..."

if [ ! -d .venv ]; then
    $PYTHON_CMD -m venv .venv
    log_ok "Virtual environment creado"
fi
source .venv/bin/activate

if command -v uv &>/dev/null; then
    uv pip install -e ".[dev]" 2>&1 | tail -3
    uv pip install aiosqlite 2>&1 | tail -1
else
    pip install -e ".[dev]" 2>&1 | tail -3
    pip install aiosqlite 2>&1 | tail -1
fi
log_ok "Dependencias Python instaladas"

# Verificar import crítico
if $PYTHON_CMD -c "from galleguimetro.main import app" 2>/dev/null; then
    log_ok "Backend importa correctamente"
else
    log_err "Error importando backend. Detalle:"
    $PYTHON_CMD -c "from galleguimetro.main import app" 2>&1
    exit 1
fi

# ---- 5. Migraciones ----
echo ""
echo "[5/7] Ejecutando migraciones..."

if alembic upgrade head 2>&1; then
    log_ok "Migraciones aplicadas"
else
    log_warn "Alembic falló. Intentando crear tablas directamente..."
    $PYTHON_CMD -c "
from galleguimetro.config.database import create_tables
create_tables()
print('  Tablas creadas con create_tables()')
"
fi

# ---- 6. Frontend ----
echo ""
echo "[6/7] Instalando dependencias frontend..."

if command -v node &>/dev/null; then
    cd frontend
    npm install 2>&1 | tail -3
    cd "$PROJECT_DIR"
    log_ok "Dependencias frontend instaladas"
else
    log_warn "Saltando frontend (Node.js no disponible)"
fi

# ---- 7. Verificación final ----
echo ""
echo "[7/7] Verificación final..."

# Test de conexión DB desde Python
$PYTHON_CMD -c "
from galleguimetro.config.database import sync_engine
with sync_engine.connect() as conn:
    result = conn.execute(__import__('sqlalchemy').text('SELECT current_database(), current_user'))
    db, user = result.fetchone()
    print(f'  DB: {db}, User: {user}')
" && log_ok "Conexión Python → PostgreSQL OK" || log_err "Fallo conexión Python → PostgreSQL"

# Verificar que el puerto 8000 está libre
if ! ss -tlnp 2>/dev/null | grep -q ":8000 "; then
    log_ok "Puerto 8000 disponible"
else
    log_warn "Puerto 8000 ya en uso"
fi

echo ""
echo "=========================================="
echo -e "  ${GREEN}Setup completo!${NC}"
echo "=========================================="
echo ""
echo "  Iniciar backend:   source .venv/bin/activate && make dev"
echo "  Iniciar frontend:  cd frontend && npm start"
echo "  Ejecutar tests:    make test"
echo ""
echo "  API docs:   http://localhost:8000/docs"
echo "  Frontend:   http://localhost:3000"
echo "  PostgreSQL: localhost:5432"
echo "  Qdrant:     http://localhost:7333/dashboard"
echo ""
echo "  DDE Bridge (desde Windows PowerShell):"
echo "    cd C:\\galleguimetro-bridge"
echo "    python dde_bridge.py --dry-run"
echo ""
