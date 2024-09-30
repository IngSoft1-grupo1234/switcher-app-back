from fastapi import APIRouter, status, HTTPException
from typing import Dict, Any
from app.crud.match_crud import MatchRepository
from app.schemas.match_schemas import MatchIn, MatchOut
from app.websocket.websocket_endpoints import player_manager

router = APIRouter(tags=["matches"])

# crea una partida ✓
@router.post("/matches/", status_code=status.HTTP_201_CREATED)
async def create_match(new_match: MatchIn):
    repo = MatchRepository()
    db_match = repo.create_match(match_name=new_match.match_name, max_players=new_match.max_players, host=new_match.host)
    player_manager.broadcast_json({
                                    "action": "games-update", 
                                    "data": {
                                                "match_id" : db_match.match_id
                                            }})
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
@router.get("/matches/notbegun", status_code=status.HTTP_200_OK, response_model=Dict[str, Any]) 
async def get_notbegun_matches()-> Dict[str, Any]:
    repo = MatchRepository()
    return repo.get_notbegun_matches()


# delete una partida ✓
@router.delete("/matches/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(match_id: int):
    repo = MatchRepository()
    match = repo.delete_match(match_id=match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")



# set has_begun a True ✓
@router.put("/matches/{match_id}/start", status_code=status.HTTP_204_NO_CONTENT)
async def start_match(match_id: int):
    repo = MatchRepository()
    match_status = repo.start_match(match_id=match_id)
    if match_status == "not enough players":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough players.")
    elif match_status == "started":
        return # no pasa nada :)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")


# set current_turn ✓
@router.put("/matches/{match_id}/turn/{turn}", status_code=status.HTTP_204_NO_CONTENT)
async def set_match_turn(match_id: int, turn: int):
    repo = MatchRepository()
    match = repo.set_match_turn(match_id=match_id, turn=turn)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")


# set player_count  ✓
@router.put("/matches/{match_id}/player_count/{player_count}", status_code=status.HTTP_204_NO_CONTENT)
async def set_player_count(match_id: int, player_count: int):
    repo = MatchRepository()
    match = repo.set_player_count(match_id=match_id, player_count=player_count)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")