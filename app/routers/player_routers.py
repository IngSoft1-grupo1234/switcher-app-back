from fastapi import APIRouter, status, HTTPException
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.schemas.player_schemas import PlayerIn, PlayerOut
from app.websocket.websocket_endpoints import player_manager
import json

router = APIRouter(tags=["players"])

# crea jugador
@router.post("/players/", response_model=PlayerOut,status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerIn) -> PlayerOut:
    repo = PlayerRepository()
    db_player = repo.create_player(username=player.username)
    return PlayerOut(username=db_player.username, player_id=db_player.player_id, operation_result="Player created successfully")

# obtiene jugador
@router.get("/players/{player_id}", response_model=PlayerOut, status_code=status.HTTP_200_OK)
async def get_player(player_id: int) -> PlayerOut:
    repo = PlayerRepository()
    db_player = repo.get_player(player_id=player_id)
    return PlayerOut(username=db_player.username, player_id=db_player.player_id, operation_result="Player found successfully")

# asigna una partida a un jugador
@router.put("/players/{player_idd}/AssignToMatch/{match_idd}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_match_to_player(player_idd: int, match_idd: int):
    repo = PlayerRepository()
    repom = MatchRepository()
    
    # ya no es abominacion
    repo.assign_match_to_player(player_id=player_idd, match_id=match_idd)
    

    db_player = repo.get_player(player_id=player_idd)

    message = {"action": "player-joined-game","data": {"playername": db_player.username,"match_id": match_idd}}
    print(f"JOIN MESSAGE: {message}")
    await player_manager.broadcast(json.dumps(message))
    

@router.put("/players/{player_id}/UnassignMatch", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_match_to_player(player_id: int):
    repo = PlayerRepository()
    
    winner_json = repo.unassign_match_to_player(player_id=player_id)
    if winner_json:
        winner_message = {"action": "game-won","data": winner_json["winner_username"]}
        print(f"WINNER MESSAGE: {winner_message}")
        await player_manager.send(json.dumps(winner_message), winner_json["winner_player_id"])

    db_player = repo.get_player(player_id=player_id)
    message = {"action": "player-left-game","data": {"playername": db_player.username,"match_id": db_player.match_id}}
    print(f"EXIT MESSAGE: {message}")
    await player_manager.broadcast(json.dumps(message))

@router.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int):
    repo = PlayerRepository()
    repo.delete_player(player_id=player_id)

@router.put("/players/use_shape_card/{shape_card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def use_shape_card(shape_card_id: int):
    repo_player = PlayerRepository()
    repo_shape_card = ShapeCardRepository()
    shape_card = repo_shape_card.get_shape_card(shape_card_id=shape_card_id)
    repo_player.use_shape_card(shape_card_id=shape_card_id)

    message = {"action": "shape-card-used","data": {"shape_card_id": shape_card.shape_card_id, "shape_card_type": shape_card.shape_card_type.value}}
    print(f"SHAPE CARD USED MESSAGE: {message}")
    await player_manager.broadcast(json.dumps(message))