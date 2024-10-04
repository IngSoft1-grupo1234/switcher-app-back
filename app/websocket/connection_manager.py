from fastapi import WebSocket
from typing import Dict, List
from fastapi import APIRouter

router = APIRouter(tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {} # Asocio el id del jugador con su websocket

    async def connect(self, websocket: WebSocket, player_id: int):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: int):
        if player_id in self.active_connections:
            del self.active_connections[player_id]

    async def send(self, data: str, player_id: int):
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_text(data)
        
    async def broadcast(self, data: str):
        for connection in self.active_connections.values():
            await connection.send_text(data)

    async def broadcast_to_id_list(self, data: str, player_id_list: List[int]):
        for player_id in player_id_list:
            if player_id in self.active_connections:
                await self.active_connections[player_id].send_text(data)



