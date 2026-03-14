# Contexto del Proyecto

## Stack autorizado

- **Backend**: Python 3.12+ con FastAPI o scripts standalone
- **Package manager**: uv (Python), pnpm (Node)
- **Bases de datos**: PostgreSQL+pgvector, Memgraph, Qdrant (self-hosted, Docker)
- **Testing**: pytest + httpx (Python), vitest (TypeScript)
- **Linting**: ruff + mypy (Python), eslint + typescript-eslint (TS)

## Estructura de directorios esperada

```
{proyecto}/
├── src/                    ← código fuente
├── tests/                  ← tests (misma estructura que src/)
├── memory-bank/            ← contexto persistente (NO ignorar)
│   ├── projectbrief.md
│   ├── productContext.md
│   ├── activeContext.md
│   ├── systemPatterns.md
│   ├── techContext.md
│   ├── progress.md
│   └── research/           ← (solo dominio académico)
├── migrations/             ← SQL migrations versionadas
├── exports/                ← outputs generados
│   ├── finance/
│   ├── design/
│   └── print3d/
├── .clinerules/            ← reglas y workflows del proyecto
├── .clineignore
├── .env.example            ← template de variables (nunca .env real)
└── pyproject.toml / package.json
```

## Variables de entorno — siempre de .env, nunca hardcodeadas

```python
import os
PG_URL = os.environ["DATABASE_URL"]  # no default para credenciales
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
```

## Dominio del proyecto

**Dominio**: software
**Descripción**: Sistema de análisis de opciones financieras en tiempo real