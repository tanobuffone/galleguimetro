"""
Galleguimetro DDE Bridge Service
=================================
Este script corre en WINDOWS NATIVO (no WSL2).
Lee datos de etrader via Excel DDE y los envía al backend en WSL2.

Uso:
    python dde_bridge.py --backend-url http://$(hostname).local:8000 --interval 5

Requisitos (instalar en Windows Python):
    pip install pywin32 requests websocket-client
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

# pywin32 - solo disponible en Windows
try:
    import win32com.client
    import pythoncom
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("ADVERTENCIA: pywin32 no instalado. Instalar con: pip install pywin32")

# WebSocket client
try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("dde_bridge.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("dde_bridge")


class EtraderDDEBridge:
    """
    Bridge entre etrader/Excel (DDE en Windows) y el backend Galleguimetro (WSL2).
    """

    def __init__(
        self,
        backend_url: str = "http://localhost:8000",
        ws_url: str = "ws://localhost:8000/ws",
        token: Optional[str] = None,
        poll_interval: float = 5.0,
        workbook_name: Optional[str] = None,
        sheet_name: str = "Sheet1",
    ):
        self.backend_url = backend_url.rstrip("/")
        self.ws_url = ws_url
        self.token = token
        self.poll_interval = poll_interval
        self.workbook_name = workbook_name
        self.sheet_name = sheet_name
        self.excel_app = None
        self.running = False
        self.ws_client = None
        self._last_data: Dict[str, Any] = {}

    @property
    def headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    # ------------------------------------------------------------------
    # Autenticación
    # ------------------------------------------------------------------

    def authenticate(self, username: str, password: str) -> bool:
        """Obtiene un JWT token del backend."""
        try:
            resp = requests.post(
                f"{self.backend_url}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self.token = data["data"]["access_token"]
            logger.info(f"Autenticado como {username}")
            return True
        except Exception as e:
            logger.error(f"Error de autenticación: {e}")
            return False

    # ------------------------------------------------------------------
    # Conexión Excel/DDE
    # ------------------------------------------------------------------

    def connect_excel(self) -> bool:
        """Conecta con la instancia de Excel que tiene los datos de etrader."""
        if not HAS_WIN32:
            logger.error("pywin32 no disponible. Ejecutar en Windows con: pip install pywin32")
            return False

        try:
            pythoncom.CoInitialize()
            # Intentar conectar a una instancia existente de Excel
            try:
                self.excel_app = win32com.client.GetObject(Class="Excel.Application")
                logger.info("Conectado a instancia existente de Excel")
            except Exception:
                # Si no hay instancia, crear una nueva
                self.excel_app = win32com.client.Dispatch("Excel.Application")
                logger.info("Creada nueva instancia de Excel")

            self.excel_app.Visible = True  # Visible para que etrader pueda interactuar
            return True
        except Exception as e:
            logger.error(f"Error conectando a Excel: {e}")
            return False

    def get_workbook(self):
        """Obtiene el workbook activo o por nombre."""
        if not self.excel_app:
            return None

        try:
            if self.workbook_name:
                for wb in self.excel_app.Workbooks:
                    if wb.Name == self.workbook_name:
                        return wb
                logger.warning(f"Workbook '{self.workbook_name}' no encontrado")
                return None
            else:
                # Usar el workbook activo
                return self.excel_app.ActiveWorkbook
        except Exception as e:
            logger.error(f"Error obteniendo workbook: {e}")
            return None

    def read_cell(self, sheet, cell_ref: str) -> Any:
        """Lee una celda de Excel de forma segura."""
        try:
            value = sheet.Range(cell_ref).Value
            return value
        except Exception:
            return None

    def read_range(self, sheet, range_ref: str) -> List[List[Any]]:
        """Lee un rango de Excel y retorna como lista de listas."""
        try:
            values = sheet.Range(range_ref).Value
            if values is None:
                return []
            if not isinstance(values, tuple):
                return [[values]]
            return [list(row) if isinstance(row, tuple) else [row] for row in values]
        except Exception as e:
            logger.error(f"Error leyendo rango {range_ref}: {e}")
            return []

    # ------------------------------------------------------------------
    # Lectura de datos de etrader/Excel
    # ------------------------------------------------------------------

    def read_market_data(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Lee datos de mercado del Excel.

        config debe tener la estructura:
        {
            "sheet": "Opciones",        # Nombre de la hoja
            "start_row": 2,             # Primera fila de datos (después del header)
            "end_row": 50,              # Última fila
            "columns": {
                "symbol": "A",          # Columna del símbolo
                "underlying": "B",      # Columna del subyacente
                "type": "C",            # call/put
                "strike": "D",          # Precio de ejercicio
                "expiration": "E",      # Fecha de vencimiento
                "last_price": "F",      # Último precio
                "bid": "G",             # Bid
                "ask": "H",             # Ask
                "volume": "I",          # Volumen
                "iv": "J",              # Volatilidad implícita
                "open_interest": "K",   # Interés abierto
            }
        }
        """
        wb = self.get_workbook()
        if not wb:
            return []

        try:
            sheet_name = config.get("sheet", self.sheet_name)
            sheet = wb.Sheets(sheet_name)
        except Exception as e:
            logger.error(f"Hoja '{sheet_name}' no encontrada: {e}")
            return []

        start_row = config.get("start_row", 2)
        end_row = config.get("end_row", 100)
        cols = config.get("columns", {})
        results = []

        for row in range(start_row, end_row + 1):
            symbol = self.read_cell(sheet, f"{cols.get('symbol', 'A')}{row}")
            if not symbol:
                continue  # Fila vacía, saltar

            option_data = {
                "symbol": str(symbol).strip(),
                "underlying_symbol": str(self.read_cell(sheet, f"{cols.get('underlying', 'B')}{row}") or "").strip(),
                "option_type": str(self.read_cell(sheet, f"{cols.get('type', 'C')}{row}") or "call").strip().lower(),
                "strike_price": float(self.read_cell(sheet, f"{cols.get('strike', 'D')}{row}") or 0),
                "last_price": float(self.read_cell(sheet, f"{cols.get('last_price', 'F')}{row}") or 0),
                "bid": float(self.read_cell(sheet, f"{cols.get('bid', 'G')}{row}") or 0),
                "ask": float(self.read_cell(sheet, f"{cols.get('ask', 'H')}{row}") or 0),
                "implied_volatility": float(self.read_cell(sheet, f"{cols.get('iv', 'J')}{row}") or 0),
                "timestamp": datetime.now().isoformat(),
            }

            # Leer fecha de vencimiento
            exp_val = self.read_cell(sheet, f"{cols.get('expiration', 'E')}{row}")
            if exp_val:
                if isinstance(exp_val, datetime):
                    option_data["expiration_date"] = exp_val.strftime("%Y-%m-%d")
                else:
                    option_data["expiration_date"] = str(exp_val)

            # Spot price del subyacente
            spot = self.read_cell(sheet, f"{cols.get('spot_price', 'L')}{row}")
            if spot:
                option_data["spot_price"] = float(spot)

            results.append(option_data)

        logger.info(f"Leídas {len(results)} opciones de Excel")
        return results

    def read_portfolio_positions(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Lee posiciones del portfolio del Excel.

        config:
        {
            "sheet": "Portfolio",
            "start_row": 2,
            "end_row": 30,
            "columns": {
                "symbol": "A",
                "quantity": "B",
                "entry_price": "C",
                "current_price": "D",
                "pnl": "E",
            }
        }
        """
        wb = self.get_workbook()
        if not wb:
            return []

        try:
            sheet = wb.Sheets(config.get("sheet", "Portfolio"))
        except Exception:
            return []

        start_row = config.get("start_row", 2)
        end_row = config.get("end_row", 50)
        cols = config.get("columns", {})
        positions = []

        for row in range(start_row, end_row + 1):
            symbol = self.read_cell(sheet, f"{cols.get('symbol', 'A')}{row}")
            if not symbol:
                continue

            position = {
                "symbol": str(symbol).strip(),
                "quantity": int(self.read_cell(sheet, f"{cols.get('quantity', 'B')}{row}") or 0),
                "entry_price": float(self.read_cell(sheet, f"{cols.get('entry_price', 'C')}{row}") or 0),
                "current_price": float(self.read_cell(sheet, f"{cols.get('current_price', 'D')}{row}") or 0),
                "unrealized_pnl": float(self.read_cell(sheet, f"{cols.get('pnl', 'E')}{row}") or 0),
                "timestamp": datetime.now().isoformat(),
            }
            positions.append(position)

        logger.info(f"Leídas {len(positions)} posiciones de Excel")
        return positions

    # ------------------------------------------------------------------
    # Envío de datos al backend (WSL2)
    # ------------------------------------------------------------------

    def push_market_data(self, data: List[Dict[str, Any]]) -> bool:
        """Envía datos de mercado al backend via HTTP POST."""
        try:
            resp = requests.post(
                f"{self.backend_url}/api/bridge/market-data",
                json={"options": data, "timestamp": datetime.now().isoformat()},
                headers=self.headers,
                timeout=10,
            )
            if resp.status_code == 200:
                result = resp.json()
                msg = result.get("message", "OK")
                logger.info(f"Market data enviada: {len(data)} opciones → {msg}")
                errors = result.get("data", {}).get("errors", [])
                for err in errors[:3]:
                    logger.warning(f"  Error en backend: {err[:120]}")
                return True
            else:
                logger.warning(f"Error enviando market data: {resp.status_code} {resp.text[:200]}")
                return False
        except requests.ConnectionError:
            logger.error(f"No se puede conectar al backend en {self.backend_url}")
            return False
        except Exception as e:
            logger.error(f"Error enviando datos: {e}")
            return False

    def push_via_websocket(self, channel: str, data: Any) -> bool:
        """Envía datos via WebSocket (si está conectado)."""
        if self.ws_client and HAS_WEBSOCKET:
            try:
                self.ws_client.send(json.dumps({
                    "type": "bridge_data",
                    "channel": channel,
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                }))
                return True
            except Exception as e:
                logger.error(f"Error WS: {e}")
        return False

    def connect_websocket(self):
        """Conecta al WebSocket del backend."""
        if not HAS_WEBSOCKET:
            logger.warning("websocket-client no instalado. Solo se usará HTTP.")
            return

        try:
            self.ws_client = websocket.WebSocket()
            self.ws_client.connect(self.ws_url)
            logger.info(f"WebSocket conectado a {self.ws_url}")
        except Exception as e:
            logger.warning(f"No se pudo conectar WebSocket: {e}. Usando solo HTTP.")
            self.ws_client = None

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------

    def run(self, market_config: Dict[str, Any], portfolio_config: Optional[Dict[str, Any]] = None):
        """
        Loop principal: lee datos de Excel y los envía al backend periódicamente.
        """
        self.running = True
        logger.info(f"Bridge iniciado. Intervalo: {self.poll_interval}s. Backend: {self.backend_url}")

        # Conectar WebSocket (opcional)
        self.connect_websocket()

        iteration = 0
        while self.running:
            try:
                iteration += 1
                logger.info(f"--- Iteración {iteration} ---")

                # Leer datos de mercado
                market_data = self.read_market_data(market_config)
                if market_data:
                    # Detectar cambios (no enviar si no cambió nada)
                    data_hash = json.dumps(market_data, sort_keys=True)
                    if data_hash != self._last_data.get("market"):
                        self._last_data["market"] = data_hash
                        self.push_market_data(market_data)
                        self.push_via_websocket("market_data", market_data)
                    else:
                        logger.info("Sin cambios en market data (datos idénticos)")

                # Leer posiciones del portfolio
                if portfolio_config:
                    positions = self.read_portfolio_positions(portfolio_config)
                    if positions:
                        pos_hash = json.dumps(positions, sort_keys=True)
                        if pos_hash != self._last_data.get("positions"):
                            self._last_data["positions"] = pos_hash
                            self.push_via_websocket("portfolio_update", positions)

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error en loop: {e}")
                time.sleep(self.poll_interval)

        self.stop()

    def stop(self):
        """Detiene el bridge."""
        self.running = False
        if self.ws_client:
            try:
                self.ws_client.close()
            except Exception:
                pass
        if self.excel_app:
            # NO cerrar Excel - etrader puede estar usándolo
            logger.info("Bridge detenido (Excel permanece abierto)")
        logger.info("Bridge detenido.")


# ------------------------------------------------------------------
# Configuración de ejemplo para etrader
# ------------------------------------------------------------------

DEFAULT_MARKET_CONFIG = {
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
        "spot_price": "L",
    },
}

DEFAULT_PORTFOLIO_CONFIG = {
    "sheet": "Portfolio",
    "start_row": 2,
    "end_row": 50,
    "columns": {
        "symbol": "A",
        "quantity": "B",
        "entry_price": "C",
        "current_price": "D",
        "pnl": "E",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Galleguimetro DDE Bridge")
    parser.add_argument("--backend-url", default="http://localhost:8000",
                        help="URL del backend (WSL2)")
    parser.add_argument("--ws-url", default="ws://localhost:8000/ws",
                        help="URL WebSocket del backend")
    parser.add_argument("--interval", type=float, default=5.0,
                        help="Intervalo de polling en segundos")
    parser.add_argument("--workbook", default=None,
                        help="Nombre del workbook de Excel (None = activo)")
    parser.add_argument("--username", default=None,
                        help="Username para autenticación")
    parser.add_argument("--password", default=None,
                        help="Password para autenticación")
    parser.add_argument("--config", default=None,
                        help="Archivo JSON con configuración de columnas")
    parser.add_argument("--dry-run", action="store_true",
                        help="Modo prueba: lee Excel pero no envía datos")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("  Galleguimetro DDE Bridge")
    logger.info("=" * 60)

    # Cargar configuración personalizada
    market_config = DEFAULT_MARKET_CONFIG
    portfolio_config = DEFAULT_PORTFOLIO_CONFIG

    if args.config:
        try:
            with open(args.config, "r") as f:
                custom_config = json.load(f)
            market_config = custom_config.get("market", market_config)
            portfolio_config = custom_config.get("portfolio", portfolio_config)
            logger.info(f"Configuración cargada desde {args.config}")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            sys.exit(1)

    # Crear bridge
    bridge = EtraderDDEBridge(
        backend_url=args.backend_url,
        ws_url=args.ws_url,
        poll_interval=args.interval,
        workbook_name=args.workbook,
    )

    # Conectar a Excel
    if not bridge.connect_excel():
        logger.error("No se pudo conectar a Excel. Abortando.")
        sys.exit(1)

    # Autenticar
    if args.username and args.password:
        if not bridge.authenticate(args.username, args.password):
            logger.error("Falló la autenticación. Abortando.")
            sys.exit(1)
    else:
        logger.warning("Sin autenticación. Algunos endpoints pueden fallar.")

    # Modo dry-run: solo leer y mostrar datos
    if args.dry_run:
        logger.info("MODO DRY-RUN: leyendo datos sin enviar al backend")
        data = bridge.read_market_data(market_config)
        print(json.dumps(data, indent=2, default=str))
        positions = bridge.read_portfolio_positions(portfolio_config)
        print(json.dumps(positions, indent=2, default=str))
        return

    # Manejar señales de interrupción
    def signal_handler(sig, frame):
        logger.info("Señal de interrupción recibida. Deteniendo...")
        bridge.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Iniciar loop
    bridge.run(market_config, portfolio_config)


if __name__ == "__main__":
    main()
