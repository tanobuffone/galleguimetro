import logging
import json
from typing import Dict, Set, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Gestor de conexiones WebSocket para actualizaciones en tiempo real."""

    def __init__(self):
        # Conexiones activas: {client_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Suscripciones por canal: {channel: set(client_ids)}
        self.subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket conectado: {client_id}")

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        # Remover de todas las suscripciones
        for channel in self.subscriptions.values():
            channel.discard(client_id)
        logger.info(f"WebSocket desconectado: {client_id}")

    def subscribe(self, client_id: str, channel: str):
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        self.subscriptions[channel].add(client_id)
        logger.info(f"Cliente {client_id} suscrito a canal: {channel}")

    def unsubscribe(self, client_id: str, channel: str):
        if channel in self.subscriptions:
            self.subscriptions[channel].discard(client_id)

    async def send_personal(self, client_id: str, data: Any):
        ws = self.active_connections.get(client_id)
        if ws:
            await ws.send_json(data)

    async def broadcast(self, channel: str, data: Any):
        """Envía datos a todos los suscriptores de un canal."""
        subscribers = self.subscriptions.get(channel, set())
        disconnected = []
        for client_id in subscribers:
            ws = self.active_connections.get(client_id)
            if ws:
                try:
                    await ws.send_json({"type": channel, "data": data})
                except Exception:
                    disconnected.append(client_id)
        # Limpiar conexiones muertas
        for client_id in disconnected:
            self.disconnect(client_id)

    async def broadcast_all(self, data: Any):
        """Envía datos a todas las conexiones activas."""
        disconnected = []
        for client_id, ws in self.active_connections.items():
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(client_id)
        for client_id in disconnected:
            self.disconnect(client_id)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


ws_manager = WebSocketManager()
