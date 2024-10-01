from fastapi import APIRouter, status, HTTPException
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository
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
    if not db_player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")
    return PlayerOut(username=db_player.username, player_id=db_player.player_id, operation_result="Player found successfully")

# asigna una partida a un jugador
@router.put("/players/{player_idd}/AssignToMatch/{match_idd}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_match_to_player(player_idd: int, match_idd: int):
    repo = PlayerRepository()
    repom = MatchRepository()
    
    #abominacion
    status_string = repo.assign_match_to_player(player_id=player_idd, match_id=match_idd)
    db_player = repo.get_player(player_id=player_idd)
    players_in_match = repom.get_player_ids_in_match(match_id=match_idd)
    
    if status_string == "match not found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
    elif status_string == "player not found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")
    elif status_string == "limit reached":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Match is full")
    elif players_in_match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
    for p in players_in_match:
        await player_manager.send(json.dumps({"action": "join-game","data": {"playername": db_player.username,"match_id": match_idd}}), p)
    

@router.put("/players/{player_id}/UnassignMatch", status_code=status.HTTP_204_NO_CONTENT)
async def unassign_match_to_player(player_id: int):
    repo = PlayerRepository()
    status_string = repo.unassign_match_to_player(player_id=player_id)
    if status_string == "Player not belong to any match":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
    elif status_string == "Player not found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")

@router.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int):
    repo = PlayerRepository()
    player = repo.delete_player(player_id=player_id)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found.")