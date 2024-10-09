from fastapi import APIRouter, status, HTTPException
from typing import List
from app.schemas.movecard_schemas import MoveCardOut
from app.crud.movecard_crud import MoveCardRepository
from app.crud.player_crud import PlayerRepository
from app.crud.shapecard_crud import ShapeCardRepository

router = APIRouter(tags=["move_cards"])

# Endpoint to retrieve move cards for a specific player
@router.get("/players/{player_id}/move_cards",status_code=status.HTTP_200_OK)
async def get_move_cards_by_player(player_id: int):
    move_card_repo = MoveCardRepository()
    move_cards = move_card_repo.get_move_cards_by_player(player_id)

    if not move_cards:
        raise HTTPException(status_code=404, detail="No move cards found for this player")
    
    return move_cards