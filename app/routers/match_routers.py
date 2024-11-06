from fastapi import APIRouter, status, HTTPException
from typing import Dict, Any
from app.crud.match_crud import MatchRepository
from app.crud.player_crud import PlayerRepository
from app.crud.movecard_crud import MoveCardRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.schemas.match_schemas import MatchIn, MatchOut
from app.websocket.websocket_endpoints import player_manager
from app.shape_detection.DFS import ShapeDetector
import json


router = APIRouter(tags=["matches"])

# crea una partida ✓
@router.post("/matches/", status_code=status.HTTP_201_CREATED)
async def create_match(new_match: MatchIn):
    matchRepo = MatchRepository()
    playerRepo = PlayerRepository()

    player = playerRepo.get_player(new_match.host) # excepcion si no existe el host
    db_match = matchRepo.create_match(match_name=new_match.match_name, max_players=new_match.max_players, host=new_match.host, password=new_match.password)
    playerRepo.assign_match_to_player(new_match.host, db_match.match_id, new_match.password)
    message = {"action": "create-game","data": {"match_id": db_match.match_id}}
    await player_manager.broadcast(json.dumps(message))
    return MatchOut(match_name=new_match.match_name, 
                    max_players=new_match.max_players, 
                    host=new_match.host,
                    match_id=db_match.match_id,
                    password=new_match.password,
                    operation_result="Succesfully created!"
                    )


# get una partida especifica ✓
@router.get("/matches/{match_idd}", status_code=status.HTTP_200_OK)
async def get_match(match_idd: int):
    repo = MatchRepository()
    match = repo.get_match_dict(match_id=match_idd)
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


# Empieza una partida inicializando los turnos, por ahora. ✓
@router.put("/matches/{match_id}/start", status_code=status.HTTP_204_NO_CONTENT)
async def start_match(match_id: int):
    repo = MatchRepository()
    movecard_repo = MoveCardRepository()
    shapecard_repo = ShapeCardRepository()
    information_to_send = repo.start_match(match_id=match_id)

    turns = information_to_send["turns"]
    board = information_to_send["board"]
    shapes = information_to_send["shapes"]

    move_cards_list = {}
    for player in turns:
        players_cards = movecard_repo.get_move_cards_by_player(player)
        move_cards_list[player] = []
        for card in players_cards:
            move_cards_list[player].append(card.move_card_type.value)
        
    # print(f"MOVE CARDS LIST 1: {move_cards_list}\n")
    
    figure_cards_list = {}
    for player in turns:
        players_cards = shapecard_repo.get_shape_cards_by_player(player)
        figure_cards_list[player] = []
        for card in players_cards:
            figure_cards_list[player].append(card.shape_card_type.value)
    # print(f"FIGURE CARDS LIST 1: {figure_cards_list}\n")
    
    lobby_message = {"action": "start-game-lobby","data": match_id}
    await player_manager.broadcast(json.dumps(lobby_message))

    game_message = {
                "action": "start-game",
                "data": 
                    {
                        "turns": turns,
                        "board": board,
                        "figure_cards": figure_cards_list,
                        "shapes": shapes
                    }
              }
    await player_manager.broadcast_to_id_list(json.dumps(game_message), turns)
    
    for player_id in turns:
        message_to_each_player = {
        "action": "start-game-card-information",
        "data": {
            "move_cards": move_cards_list[player_id]
        }
        }   

        await player_manager.send(json.dumps(message_to_each_player), player_id)


@router.get("/matches/{match_id}/start", status_code=status.HTTP_200_OK)
async def get_match_start_info(match_id: int):
    repo = MatchRepository()
    movecard_repo = MoveCardRepository()
    shapecard_repo = ShapeCardRepository()
    turns = repo.get_turns(match_id=match_id)
    board = repo.get_board(match_id=match_id)
    shapes = ShapeDetector().test_shape_fitting(board)
    move_cards_list = {}
    for player in turns:
        players_cards = movecard_repo.get_move_cards_by_player(player)
        move_cards_list[player] = []
        for card in players_cards:
            move_cards_list[player].append(card.move_card_type.value)
    figure_cards_list = {}
    for player in turns:
        players_cards = shapecard_repo.get_shape_cards_by_player(player)
        figure_cards_list[player] = []
        for card in players_cards:
            figure_cards_list[player].append({"id": card.shape_card_id, "type": card.shape_card_type.value})
    return {"turns": turns, "board": board, "move_cards": move_cards_list, "figure_cards": figure_cards_list, "shapes": shapes}


# Pasa el turno al siguiente jugador ✓ 
@router.put("/matches/{match_id}/next_turn", status_code=status.HTTP_204_NO_CONTENT)
async def pass_turn(match_id):
    repo = MatchRepository()
    next_player_json = repo.get_next_player(match_id=match_id)

    # what, get_next_player ya maneja estas excepciones
    if next_player_json is None:
        raise HTTPException(status_code=404, detail="Match not found.")
    elif not next_player_json: 
        raise HTTPException(status_code=400, detail="No next player available.")

    updated_board, shapes = repo.pass_turn(match_id=match_id)

    message = {"action": "next-turn", "data": {"next_player_name":next_player_json["username"], "next_player_id": next_player_json["player_id"]}}
    print(f"<> <> <> <> NEXT TURN MESSAGE: {json.dumps(message)}")
    ids_from_match = repo.get_player_ids_in_match(match_id=match_id)
    await player_manager.broadcast_to_id_list(json.dumps(message), ids_from_match)

    board_message = {"action": "update-board", "data": {"board": updated_board, "shapes": shapes}}
    print(f"NEXT TURN BOARD MESSAGE: {board_message}")
    await player_manager.broadcast_to_id_list(json.dumps(board_message), ids_from_match)

    