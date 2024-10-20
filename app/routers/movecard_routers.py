from fastapi import APIRouter, status, HTTPException
from typing import List
from app.schemas.movecard_schemas import MoveCardOut, MoveCardIn, MoveCardPreview
from app.crud.movecard_crud import MoveCardRepository
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.websocket.websocket_endpoints import player_manager
import json

router = APIRouter(tags=["move_cards"])

# Endpoint to retrieve move cards for a specific player
@router.get("/players/{player_id}/move_cards",status_code=status.HTTP_200_OK)
async def get_move_cards_by_player(player_id: int):
    move_card_repo = MoveCardRepository()
    move_cards = move_card_repo.get_move_cards_by_player(player_id)

    if not move_cards:
        raise HTTPException(status_code=404, detail="No move cards found for this player")
    
    return move_cards

# Endpoint para utilizar una carta movimiento
@router.put("/players/{player_id}/move_cards/{move_card_id}/use",status_code=status.HTTP_204_NO_CONTENT)
async def soft_move(player_id: int, move_card_id: int, movement_info: MoveCardIn):
    move_card_repo = MoveCardRepository()
    updated_board, shapes = move_card_repo.soft_move(player_id, move_card_id, movement_info)    

    repo = MatchRepository()
    player_repo = PlayerRepository()
    match_id = player_repo.get_player(player_id).match_id
    ids_from_match = repo.get_player_ids_in_match(match_id=match_id)
    message = {"action": "update-board", "data": {"board": updated_board, "shapes": shapes}}
    print(f"SOFT_MOVE_WEBSOCKET: {message}")
    await player_manager.broadcast_to_id_list(json.dumps(message), ids_from_match)

# Endpoint para cancelar movimiento parcial
@router.put("/players/{player_id}/move_cards/cancel",status_code=status.HTTP_204_NO_CONTENT)
async def cancel_soft_move(player_id: int):
    move_card_repo = MoveCardRepository()
    updated_board, shapes = move_card_repo.cancel_soft_move(player_id)

    repo = MatchRepository()
    player_repo = PlayerRepository()
    match_id = player_repo.get_player(player_id).match_id
    ids_from_match = repo.get_player_ids_in_match(match_id=match_id)
    message = {"action": "update-board", "data": {"board": updated_board, "shapes": shapes}}
    print(f"CANCEL_MOVE_WEBSOCKET: {message}")
    await player_manager.broadcast_to_id_list(json.dumps(message), ids_from_match)

# Endpoint para previsualizar movimientos de una carta
@router.put("/move_cards/preview",status_code=status.HTTP_200_OK)
async def preview_move_card(movement_info: MoveCardPreview):
    move_card_repo = MoveCardRepository()
    dict = move_card_repo.preview_move_card(movement_info)
    print(f"PREVIEW_MOVE_CARD: {dict}")
    return dict
    