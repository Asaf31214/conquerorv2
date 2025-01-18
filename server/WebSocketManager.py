from fastapi import WebSocket, WebSocketDisconnect
from typing_extensions import Any, Dict, List


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, data: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except WebSocketDisconnect:
                await self.disconnect(connection)

    async def cleanup(self):
        for connection in self.active_connections:
            await self.disconnect(connection)
