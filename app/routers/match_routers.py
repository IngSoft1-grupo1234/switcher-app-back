from fastapi import APIRouter, status, HTTPException
from typing import Dict, Any
from app.crud.match_crud import MatchRepository
from app.crud.player_crud import PlayerRepository
from app.crud.movecard_crud import MoveCardRepository
from app.schemas.match_schemas import MatchIn, MatchOut
from app.websocket.websocket_endpoints import player_manager
import json


router = APIRouter(tags=["matches"])

# crea una partida ✓
@router.post("/matches/", status_code=status.HTTP_201_CREATED)
async def create_match(new_match: MatchIn):
    matchRepo = MatchRepository()
    playerRepo = PlayerRepository()

    db_match = matchRepo.create_match(match_name=new_match.match_name, max_players=new_match.max_players, host=new_match.host)
    playerRepo.assign_match_to_player(new_match.host, db_match.match_id)
    message = {"action": "create-game","data": {"match_id": db_match.match_id}}
    await player_manager.broadcast(json.dumps(message))
    return MatchOut(match_name=new_match.match_name, 
                    max_players=new_match.max_players, 
                    host=new_match.host,
                    match_id=db_match.match_id,
                    operation_result="Succesfully created!"
                    )


# get una partida especifica ✓
@router.get("/matches/{match_idd}", status_code=status.HTTP_200_OK)
async def get_match(match_idd: int):
    repo = MatchRepository()
    match = repo.get_match(match_id=match_idd)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")

    return match


# get todas las partidas ✓
@router.get("/matches/", status_code=status.HTTP_200_OK, response_model=Dict[str, Any]) 
async def get_all_matches()-> Dict[str, Any]:
    repo = MatchRepository()
    return repo.get_all_matches()
    

# get todos los "lobbies" o partidas no iniciadas ✓
@router.get("/matches/notbegun/", status_code=status.HTTP_200_OK, response_model=Dict[str, Any]) 
async def get_notbegun_matches()-> Dict[str, Any]:
    repo = MatchRepository()
    return repo.get_notbegun_matches()


# delete una partida ✓
@router.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(match_id: int):
    repo = MatchRepository()
    repo.delete_match(match_id=match_id)


# Empieza una partida inicializando los turnos, por ahora. ✓
@router.put("/matches/{match_id}/start", status_code=status.HTTP_204_NO_CONTENT)
async def start_match(match_id: int):
    repo = MatchRepository()
    information_to_send = repo.start_match(match_id=match_id)
    message = {"action": "start-game","data": {"turns": information_to_send}}
    # print(f"<> <> <> <> START MATCH MESSAGE: {json.dumps(message)}")
    await player_manager.broadcast_to_id_list(json.dumps(message), information_to_send) # chanchada

# set current_turn ✓ 
# Deberia ser cambiado a "advance turn" que avance al siguiente turno dentro de la lista de turnos /!\ /!\ /!\
@router.put("/matches/{match_id}/turn/{turn}", status_code=status.HTTP_204_NO_CONTENT)
async def set_match_turn(match_id: int, turn: int):
    repo = MatchRepository()
    repo.set_match_turn(match_id=match_id, turn=turn)


# set player_count  ✓
@router.put("/matches/{match_id}/player_count/{player_count}", status_code=status.HTTP_204_NO_CONTENT)
async def set_player_count(match_id: int, player_count: int):
    repo = MatchRepository()
    repo.set_player_count(match_id=match_id, player_count=player_count)
    