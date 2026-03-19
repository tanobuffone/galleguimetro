# Galleguimetro DDE Bridge

Bridge entre etrader/Excel (Windows 11) y el backend Galleguimetro (WSL2).

## Arquitectura

```
etrader v3.75.9 (Win11)
    ↓ Datos de mercado en tiempo real
Excel (Win11) - con fórmulas DDE vinculadas a etrader
    ↓ win32com (COM automation)
dde_bridge.py (Python en Windows nativo)
    ↓ HTTP POST cada N segundos
FastAPI Backend (WSL2 Ubuntu)
    ↓ WebSocket broadcast
React Frontend (WSL2)
```

## Requisitos (Windows)

- Python 3.11+ instalado **en Windows** (no WSL)
  - Descargar de https://www.python.org/downloads/
- Excel con libro abierto que recibe datos de etrader via DDE
- etrader v3.75.9 corriendo y conectado

## Instalación (en PowerShell de Windows)

```powershell
# 1. Navegar al directorio del bridge
cd \\wsl$\Ubuntu\home\gdrick\galleguimetro\bridge

# O copiar el bridge a una carpeta de Windows
mkdir C:\galleguimetro-bridge
copy \\wsl$\Ubuntu\home\gdrick\galleguimetro\bridge\* C:\galleguimetro-bridge\
cd C:\galleguimetro-bridge

# 2. Crear venv de Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install pywin32 requests websocket-client
```

## Configuración

Copiar `bridge_config.example.json` a `bridge_config.json` y ajustar las columnas
según la estructura de tu Excel con datos de etrader:

```json
{
  "market": {
    "sheet": "Opciones",
    "start_row": 2,
    "end_row": 100,
    "columns": {
      "symbol": "A",
      "underlying": "B",
      "type": "C",
      "strike": "D",
      "expiration": "E",
      "last_price": "F",
      "bid": "G",
      "ask": "H",
      "volume": "I",
      "iv": "J",
      "open_interest": "K",
      "spot_price": "L"
    }
  }
}
```

### Mapeo de columnas Excel ↔ Bridge

Adaptar según tu hoja de Excel. Por ejemplo, si tu hoja tiene:

| Col | Header en Excel     | Campo en config   |
|-----|---------------------|-------------------|
| A   | Ticker              | symbol            |
| B   | Subyacente          | underlying        |
| C   | Tipo (C/P)          | type              |
| D   | Strike              | strike            |
| E   | Vencimiento         | expiration        |
| F   | Último              | last_price        |
| G   | Bid                 | bid               |
| H   | Ask                 | ask               |
| I   | Vol                 | volume            |
| J   | VI                  | iv                |
| K   | OI                  | open_interest     |
| L   | Spot                | spot_price        |

## Uso

### Obtener la IP de WSL2 desde Windows

```powershell
# La IP de WSL2 cambia en cada reinicio
wsl hostname -I
# Ejemplo resultado: 172.25.176.1
```

O usar `localhost` que en Win11 rutea automáticamente a WSL2.

### Modo Dry-Run (primero probar sin enviar datos)

```powershell
python dde_bridge.py --dry-run
```

Esto lee datos de Excel y los muestra en consola, sin enviar al backend.
**Usar esto primero para verificar que lee correctamente.**

### Ejecutar el bridge

```powershell
# Opción A: localhost (Win11 rutea a WSL2 automáticamente)
python dde_bridge.py \
  --backend-url http://localhost:8000 \
  --username tu_usuario \
  --password tu_password \
  --interval 5 \
  --config bridge_config.json

# Opción B: IP explícita de WSL2
python dde_bridge.py \
  --backend-url http://172.25.176.1:8000 \
  --username tu_usuario \
  --password tu_password \
  --interval 3

# Opción C: con workbook específico
python dde_bridge.py \
  --backend-url http://localhost:8000 \
  --workbook "MiPortfolio.xlsx" \
  --username admin \
  --password admin123 \
  --interval 5
```

### Parámetros

| Parámetro       | Default                    | Descripción                           |
|-----------------|----------------------------|---------------------------------------|
| --backend-url   | http://localhost:8000      | URL del backend FastAPI en WSL2       |
| --ws-url        | ws://localhost:8000/ws     | URL WebSocket del backend             |
| --interval      | 5.0                        | Segundos entre lecturas de Excel      |
| --workbook      | (activo)                   | Nombre del workbook (None = activo)   |
| --username      | -                          | Usuario para auth JWT                 |
| --password      | -                          | Password para auth JWT                |
| --config        | -                          | Archivo JSON de configuración         |
| --dry-run       | false                      | Solo leer Excel, no enviar datos      |

## Testeo paso a paso

### Paso 1: Verificar que el backend responde

Desde Windows PowerShell:
```powershell
curl http://localhost:8000/health
# Debe retornar: {"success": true, "message": "Servicios operativos", ...}
```

### Paso 2: Crear usuario de prueba

```powershell
curl -X POST http://localhost:8000/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{"username":"bridge_user","email":"bridge@test.com","password":"bridgepass123"}'
```

### Paso 3: Dry-run del bridge

```powershell
python dde_bridge.py --dry-run
```

Verificar que los datos se leen correctamente del Excel.

### Paso 4: Ejecutar bridge real

```powershell
python dde_bridge.py --username bridge_user --password bridgepass123 --interval 5
```

### Paso 5: Verificar en el dashboard

Abrir http://localhost:3000 en el navegador. Los datos de opciones deben aparecer
actualizándose cada 5 segundos.

## Troubleshooting

### "No se puede conectar al backend"
- Verificar que el backend está corriendo: `curl http://localhost:8000/health`
- En Win11, `localhost` debería rutear a WSL2. Si no funciona, usar la IP de WSL2
- Verificar firewall de Windows

### "pywin32 no instalado"
- Asegurarse de usar Python de **Windows** (no WSL)
- `pip install pywin32`
- Si falla, descargar el instalador de https://github.com/mhammond/pywin32/releases

### "Workbook no encontrado"
- Excel debe estar abierto con el libro antes de iniciar el bridge
- Usar `--workbook "NombreExacto.xlsx"` (case sensitive)

### "Error de autenticación"
- Primero crear el usuario via la API o el frontend
- Verificar que username/password son correctos

### Excel se congela
- El bridge lee datos sin modificar - no debería congelar Excel
- Aumentar el `--interval` a 10 o más segundos
- Verificar que no hay macros conflictivas
