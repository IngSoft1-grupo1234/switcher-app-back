from fastapi import APIRouter, status, HTTPException
from app.crud.player_crud import PlayerRepository
from app.crud.match_crud import MatchRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.schemas.player_schemas import PlayerIn, PlayerOut, Password, LogIn
from app.schemas.chat_schemas import ChatIn
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
async def assign_match_to_player(player_idd: int, match_idd: int, password: Password = Password(password="")):
    repo = PlayerRepository()
    repom = MatchRepository()
    
    # ya no es abominacion
    repo.assign_match_to_player(player_id=player_idd, match_id=match_idd, password=password.password)
    

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
            try:
                next_player_json = repo_match.get_next_player(match_id=player.match_id) # error cuando solo queda un jugador y abandona?
            except HTTPException:
                next_player_json = {"username": player.username, "player_id": player_id}
            repo_match.pass_turn(player.match_id)
            if next_player_json:
                message = {"action": "next-turn",
                            "data": {"next_player_name":next_player_json["username"],
                                      "next_player_id": next_player_json["player_id"]}
                          }
                await player_manager.broadcast(json.dumps(message)) # esto no estaba antes T-T, nadie se queja loco

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
                                                    "prohibited_color": prohibited_color,
                                                    "player_id": player_id}}
    print(f"SHAPE CARD USED MESSAGE: {message}")
    await player_manager.broadcast(json.dumps(message))
    
    
    
    message = {"action": "update-board", "data": {"board": board, "shapes": shapes}}
    print(f"UPDATE BOARD MESSAGE from shape card use: {message}")
    await player_manager.broadcast_to_id_list(json.dumps(message), match.turns)

    winner_json = repo_player.winner_without_shape_card(player_id=player_id)
    if winner_json:
        winner_message = {"action": "game-won","data": {"playername": winner_json["winner_username"],
                                                        "player_id": winner_json["winner_player_id"]}}
        print(f"WINNER MESSAGE: {winner_message}")
        await player_manager.broadcast(json.dumps(winner_message))


@router.put("/players/{player_id}/send_message", status_code=status.HTTP_204_NO_CONTENT)
async def send_message(player_id: int, message_info: ChatIn):
    repo = PlayerRepository()
    repo.player_send_message(player_id=player_id, content=message_info.content)
    # player_cruds hace el broadcast_to_id_list    


@router.put("/players/block_shape_card/{shape_card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def block_shape_card(shape_card_id: int, usedshape: UsedShapeSchema):
    repo_player = PlayerRepository()
    repo_shape_card = ShapeCardRepository()
    shape_card = repo_shape_card.get_shape_card(shape_card_id=shape_card_id)
    player_block = repo_player.get_player(player_id=shape_card.player_id)
    player_id, prohibited_color = repo_player.block_shape_card(shape_card_id=shape_card_id, color=usedshape.color)
    player_turn = repo_player.get_player(player_id=player_id)

    message = {"action": "shape-card-block","data": {   "shape_card_id": shape_card.shape_card_id, 
                                                        "shape_card_type": shape_card.shape_card_type.value, 
                                                        "player_turn_id": player_turn.player_id, 
                                                        "player_turn_name": player_turn.username, 
                                                        "player_block_id": player_block.player_id, 
                                                        "player_block_name": player_block.username,
                                                        "prohibited_color": prohibited_color
                                                    }}
    print(f"SHAPE CARD BLOCK MESSAGE: {message}")
    await player_manager.broadcast(json.dumps(message))
