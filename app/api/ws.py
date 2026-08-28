"""
WebSocket connection manager for real-time live alert and forecast broadcasts.
"""
from typing import List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger("websocket_manager")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active: {len(self.active_connections)}")

    async def broadcast_json(self, data: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data))
            except Exception:
                disconnected.append(connection)
        for dead in disconnected:
            self.disconnect(dead)

ws_manager = ConnectionManager()
