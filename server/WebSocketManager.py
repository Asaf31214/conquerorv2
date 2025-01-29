from fastapi import WebSocket, WebSocketDisconnect
from typing_extensions import Any, Dict, List


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        await websocket.accept()
        self.active_connections[game_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, game_id: str):
        if game_id in self.active_connections:
            try:
                self.active_connections[game_id].remove(websocket)
            except ValueError:
                pass

    async def broadcast(self, data: Dict[str, Any], game_id: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(data)
                except WebSocketDisconnect:
                    await self.disconnect(connection, game_id)

    async def cleanup_game(self, game_id: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                await self.disconnect(connection, game_id)
            del self.active_connections[game_id]

    async def cleanup(self):
        for game_id in self.active_connections:
            await self.cleanup_game(game_id)
