"""
Excel DDE Service - servicio para conectar con Excel via DDE en Windows.
La clase ExcelDDEService se mantiene en galleguimetro/services/ original.
Este archivo es un wrapper de compatibilidad.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ExcelDDEService:
    """Servicio DDE para conexión con Excel (solo Windows)."""

    def __init__(self):
        self.excel_app = None
        self.workbooks = {}
        self.connections = {}

    def initialize(self) -> bool:
        try:
            import win32com.client
            self.excel_app = win32com.client.Dispatch("Excel.Application")
            self.excel_app.Visible = False
            logger.info("Conexión DDE con Excel establecida")
            return True
        except ImportError:
            logger.warning("pywin32 no disponible - DDE solo funciona en Windows")
            return False
        except Exception as e:
            logger.error(f"Error inicializando DDE: {e}")
            return False

    def get_portfolio_data(self, workbook_name: str, portfolio_id: str) -> List[Dict[str, Any]]:
        logger.debug(f"DDE get_portfolio_data: {workbook_name}/{portfolio_id}")
        return []

    def close(self) -> bool:
        if self.excel_app:
            try:
                self.excel_app.Quit()
            except Exception:
                pass
            self.excel_app = None
        return True


def get_dde_service() -> ExcelDDEService:
    return ExcelDDEService()
