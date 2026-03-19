# === Backend Dockerfile ===
FROM python:3.11-slim as base

WORKDIR /app

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install --no-cache-dir uv

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock* ./

# Instalar dependencias Python
RUN uv pip install --system -e ".[dev]"

# === Desarrollo ===
FROM base as development
COPY . .
CMD ["uvicorn", "galleguimetro.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# === Producción ===
FROM base as production
COPY galleguimetro/ ./galleguimetro/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Ejecutar migraciones y luego el servidor
CMD ["sh", "-c", "alembic upgrade head && uvicorn galleguimetro.main:app --host 0.0.0.0 --port 8000 --workers 4"]
