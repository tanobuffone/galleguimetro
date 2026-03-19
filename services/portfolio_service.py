"""
Legacy portfolio service - mantenido para compatibilidad.
La lógica CRUD ahora está en galleguimetro/repositories/portfolio_repo.py
y galleguimetro/repositories/position_repo.py.
"""
import logging

logger = logging.getLogger(__name__)
logger.info("Legacy portfolio_service.py - usar repositories/ en su lugar.")
