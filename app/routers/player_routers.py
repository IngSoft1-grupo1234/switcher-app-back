from fastapi import APIRouter, status, HTTPException
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.schemas.player_schemas import PlayerIn, PlayerOut
from app.websocket.websocket_endpoints import player_manager
from app.schemas.shapecard_schemas import UsedShapeSchema
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
    repo_player = PlayerRepository()
    repo_match = MatchRepository()
    player = repo_player.get_player(player_id=player_id)
    
    if repo_player.is_player_turn(player_id):
        if repo_player.is_player_turn(player_id) != "bazinga":
            repo_match.pass_turn(player.match_id)

    winner_json = repo_player.unassign_match_to_player(player_id=player_id)
    if winner_json:
        winner_message = {"action": "game-won","data": winner_json["winner_username"]}
        print(f"WINNER MESSAGE: {winner_message}")
        await player_manager.send(json.dumps(winner_message), winner_json["winner_player_id"])

    db_player = repo_player.get_player(player_id=player_id)
    message = {"action": "player-left-game","data": {"playername": db_player.username,"match_id": db_player.match_id, "player_id": db_player.player_id}}    
    print(f"EXIT MESSAGE: {message}")
    await player_manager.broadcast(json.dumps(message))

@router.delete("/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int):
    repo = PlayerRepository()
    repo.delete_player(player_id=player_id)


@router.put("/players/use_shape_card/{shape_card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def use_shape_card(shape_card_id: int, usedshape: UsedShapeSchema):
    repo_player = PlayerRepository()
    match_repo = MatchRepository()

    repo_shape_card = ShapeCardRepository()
    shape_card = repo_shape_card.get_shape_card(shape_card_id=shape_card_id)
    board, shapes, prohibited_color = repo_player.use_shape_card(shape_card_id=shape_card_id, color=usedshape.color, location=usedshape.location)
    player_id = shape_card.player_id

    player = repo_player.get_player(player_id=player_id)
    match = match_repo.get_match(player.match_id)

    message = {"action": "shape-card-used","data": {"shape_card_id": shape_card.shape_card_id,
                                                    "shape_card_type": shape_card.shape_card_type.value,
                                                    "prohibited_color": prohibited_color,}}
    print(f"SHAPE CARD USED MESSAGE: {message}")
    await player_manager.broadcast_to_id_list(json.dumps(message), match.turns)
    
    
    
    message = {"action": "update-board", "data": {"board": board, "shapes": shapes}}
    print(f"UPDATE BOARD MESSAGE from shape card use: {message}")
    await player_manager.broadcast_to_id_list(json.dumps(message), match.turns)

    winner_json = repo_player.winner_without_shape_card(player_id=player_id)
    if winner_json:
        winner_message = {"action": "game-won","data": {"playername": winner_json["winner_username"], "player_id": winner_json["winner_player_id"]}}
        print(f"WINNER MESSAGE: {winner_message}")
        await player_manager.broadcast(json.dumps(winner_message))
