# Galleguimetro - Guía de Primer Deploy

## Entorno

| Componente | Dónde corre |
|---|---|
| etrader v3.75.9 | Windows 11 nativo |
| Excel (con DDE) | Windows 11 nativo |
| DDE Bridge | Windows 11 nativo (Python) |
| Backend FastAPI | WSL2 Ubuntu Noble |
| PostgreSQL + Qdrant | WSL2 (Docker) |
| Frontend React | WSL2 |

---

## PARTE 1: Setup del Backend (WSL2)

### 1.1 Requisitos previos

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Python 3.11+
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Docker (si no está instalado)
# https://docs.docker.com/engine/install/ubuntu/

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Build tools
sudo apt install -y build-essential libpq-dev
```

### 1.2 Setup automático

```bash
cd ~/galleguimetro
chmod +x scripts/setup-wsl2.sh
./scripts/setup-wsl2.sh
```

### 1.3 Setup manual (si prefieres paso a paso)

```bash
cd ~/galleguimetro

# 1. Crear .env
cp .env.example .env
# Editar .env: ajustar SECRET_KEY, DATABASE_URL, etc.

# 2. Iniciar Docker (PostgreSQL + Qdrant)
docker compose up -d

# 3. Instalar dependencias Python
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -e ".[dev]"

# 4. Ejecutar migraciones
alembic upgrade head

# 5. Instalar frontend
cd frontend && npm install && cd ..
```

### 1.4 Iniciar servicios

Terminal 1 - Backend:
```bash
cd ~/galleguimetro
source .venv/bin/activate
make dev
# → http://localhost:8000/docs
```

Terminal 2 - Frontend:
```bash
cd ~/galleguimetro/frontend
npm start
# → http://localhost:3000
```

### 1.5 Verificar

```bash
# Health check
curl http://localhost:8000/health

# Crear primer usuario
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@galleguimetro.app","password":"admin12345","full_name":"Admin"}'

# Probar griegas
curl -X POST http://localhost:8000/test/greeks
```

---

## PARTE 2: Setup del DDE Bridge (Windows 11)

### 2.1 Instalar Python en Windows

Descargar e instalar Python 3.11+ desde https://www.python.org/downloads/
- Marcar "Add Python to PATH"
- Instalar para "All Users"

### 2.2 Preparar el bridge

Abrir **PowerShell** (no WSL):

```powershell
# Crear directorio de trabajo en Windows
mkdir C:\galleguimetro-bridge
cd C:\galleguimetro-bridge

# Copiar archivos del bridge desde WSL2
copy \\wsl$\Ubuntu\home\gdrick\galleguimetro\bridge\dde_bridge.py .
copy \\wsl$\Ubuntu\home\gdrick\galleguimetro\bridge\bridge_config.example.json bridge_config.json

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install pywin32 requests websocket-client
```

### 2.3 Configurar mapeo de columnas

Editar `bridge_config.json` para que coincida con la estructura de tu Excel.

Abrir tu Excel que recibe datos de etrader y anotar qué columna tiene cada dato:
- ¿En qué hoja están las opciones? → `"sheet": "NombreDeLaHoja"`
- ¿Desde qué fila empiezan los datos? → `"start_row": 2` (si fila 1 es header)
- ¿En qué columna está el símbolo? → `"symbol": "A"` (o B, C, etc.)

### 2.4 Verificar conectividad Win11 → WSL2

```powershell
# Verificar que el backend responde desde Windows
curl http://localhost:8000/health

# Si localhost no funciona, obtener IP de WSL2:
wsl hostname -I
# Luego usar esa IP: curl http://172.x.x.x:8000/health
```

**Nota Win11**: En Windows 11, `localhost` rutea automáticamente a WSL2 (localhost forwarding).

### 2.5 Test del bridge (dry-run)

```powershell
cd C:\galleguimetro-bridge
.\venv\Scripts\Activate.ps1

# Abrir etrader + Excel ANTES de ejecutar esto

# Dry-run: lee Excel y muestra datos, sin enviar al backend
python dde_bridge.py --dry-run --config bridge_config.json
```

Verificar que la salida muestra las opciones correctamente. Ejemplo:
```json
[
  {
    "symbol": "GGAL240315C00200",
    "underlying_symbol": "GGAL",
    "option_type": "call",
    "strike_price": 200.0,
    "last_price": 15.50,
    "bid": 15.00,
    "ask": 16.00,
    "implied_volatility": 0.45
  }
]
```

### 2.6 Ejecutar el bridge

```powershell
# Con autenticación
python dde_bridge.py `
  --backend-url http://localhost:8000 `
  --username admin `
  --password admin12345 `
  --interval 5 `
  --config bridge_config.json

# Con workbook específico (si tienes varios abiertos)
python dde_bridge.py `
  --backend-url http://localhost:8000 `
  --workbook "etrader_opciones.xlsx" `
  --username admin `
  --password admin12345 `
  --interval 3
```

El bridge mostrará:
```
2026-03-18 10:00:00 [INFO] Bridge iniciado. Intervalo: 5.0s
2026-03-18 10:00:00 [INFO] Conectado a instancia existente de Excel
2026-03-18 10:00:00 [INFO] Autenticado como admin
2026-03-18 10:00:05 [INFO] --- Iteración 1 ---
2026-03-18 10:00:05 [INFO] Leídas 45 opciones de Excel
2026-03-18 10:00:05 [DEBUG] Market data enviada: 45 opciones
```

---

## PARTE 3: Verificación end-to-end

### 3.1 Flujo completo

1. **etrader** actualiza precios en **Excel** via DDE
2. **dde_bridge.py** (Windows) lee Excel cada N segundos
3. Bridge envía datos via HTTP POST a **FastAPI** (WSL2)
4. FastAPI persiste en **PostgreSQL** y broadcastea via **WebSocket**
5. **React frontend** recibe actualización y refresca UI

### 3.2 Verificar datos en el backend

```bash
# Desde WSL2, verificar opciones creadas
curl -s http://localhost:8000/api/options \
  -H "Authorization: Bearer TU_TOKEN" | python3 -m json.tool

# Verificar status del bridge
curl http://localhost:8000/api/bridge/status
```

### 3.3 Verificar en el frontend

1. Abrir http://localhost:3000
2. Login con las credenciales creadas
3. Ir a "Gestión de Opciones" - deben aparecer las opciones de etrader
4. Ir a "Dashboard" - deben verse los charts actualizándose

---

## PARTE 4: Operación diaria

### Orden de inicio

```
1. Iniciar Docker:                    docker compose up -d  (WSL2)
2. Iniciar backend:                   make dev              (WSL2)
3. Iniciar frontend:                  cd frontend && npm start (WSL2)
4. Abrir etrader + Excel              (Windows)
5. Iniciar bridge:                    python dde_bridge.py  (Windows)
```

### Orden de parada

```
1. Ctrl+C en el bridge               (Windows)
2. Ctrl+C en el frontend             (WSL2)
3. Ctrl+C en el backend              (WSL2)
4. docker compose down               (WSL2, opcional)
```

---

## Troubleshooting

### El bridge no puede conectar al backend
```powershell
# Verificar que WSL2 está corriendo
wsl --status

# Verificar que el backend responde
curl http://localhost:8000/health

# Si localhost no funciona, usar IP directa
wsl hostname -I
```

### Error "QuantLib" al iniciar backend
```bash
# QuantLib requiere compilación
pip install quantlib
# Si falla, instalar binarios:
sudo apt install -y libquantlib0-dev
pip install QuantLib-Python
```

### Excel se congela con el bridge
- Subir el intervalo: `--interval 10` o más
- Verificar que no hay macros pesadas corriendo al mismo tiempo
- El bridge usa COM automation read-only, no debería interferir

### Datos no aparecen en el frontend
1. Verificar en /docs que el endpoint `/api/bridge/market-data` devuelve 200
2. Verificar que el usuario del bridge tiene token válido
3. Abrir DevTools del browser → Network → verificar que las requests a /api/ funcionan
4. Revisar la consola del backend para errores
