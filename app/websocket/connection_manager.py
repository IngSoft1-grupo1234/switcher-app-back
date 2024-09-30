from fastapi import WebSocket
from typing import Dict
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

    async def send_json(self, data: dict, player_id: int):
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_json(data)
        
    async def broadcast_json(self, data: dict):
        for connection in self.active_connections.values():
            await connection.send_json(data)



# async def handle_message(player_id: int, message: dict, manager: ConneectionManager):
#     action = message.get("action")
#     if action == "send-user-id":
#         await manager.broadcast(f"Player {data['username']} with Id {data['userId']} connected")
#     else:
#         await manager.send_personal_message(f"Unknown action: {action}", player_id)
