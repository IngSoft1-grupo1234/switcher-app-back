from fastapi import APIRouter, status, HTTPException
from typing import List
from app.schemas import MoveCard
from app.crud import get_move_cards_by_player

router = APIRouter(tags=["move_cards"])


# Endpoint to retrieve move cards for a specific player
@router.get("/players/{player_id}/move_cards", response_model=List[MoveCard],status_code=status.HTTP_200_OK)
def get_move_cards_by_player(player_id: int):
    move_cards = get_move_cards_by_player(player_id)
    if not move_cards:
        raise HTTPException(status_code=404, detail="No move cards found for this player")
    return move_cards