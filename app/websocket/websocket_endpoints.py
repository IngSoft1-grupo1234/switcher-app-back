from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.connection_manager import ConnectionManager
import asyncio


router = APIRouter(tags=["websocket"])

player_manager = ConnectionManager()
# Websocket para cada jugador
@router.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int):
    await player_manager.connect(websocket, player_id)
    while True:
        try:
           data = await websocket.receive_text()
        except WebSocketDisconnect:
            player_manager.disconnect(player_id)
            break