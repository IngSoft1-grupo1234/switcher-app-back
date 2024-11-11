from app.models.player_models import Player as PlayerModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.schemas.movecard_schemas import MoveCardIn, MoveCardPreview
from app.models.movecard_models import MoveCardType
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
from app.models.match_models import Match as MatchModel
from app.models.chat_models import messageType
from app.database import session
from fastapi import HTTPException
import json
import asyncio
from app.crud.player_crud import PlayerRepository
from app.shape_detection.DFS import ShapeDetector

from app.crud.shapecard_crud import ShapeCardRepository

class MoveCardRepository:
    def create_move_card(self, match_id: int, move_card_type: MoveCardType):
        db = session()
        try:
            try     :
                move_card_type = MoveCardType(move_card_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Move card type does not exist")
            
            move_card_count = db.query(MoveCardModel).filter(
                MoveCardModel.move_card_type == move_card_type,
                MoveCardModel.match_id == match_id
            ).count()
            if isinstance(move_card_count, int) and move_card_count >= 7:
                raise HTTPException(status_code=400, detail="Cannot create more than 7 move cards of the same type")
            
            move_card = MoveCardModel(match_id=match_id, move_card_type=move_card_type)
            db.add(move_card)
            db.commit()
            db.refresh(move_card)
            return move_card.move_card_id
        finally:
            db.close()
        
    def get_move_cards_id_in_match(self, match_id: int):
        db = session()
        try:
            move_cards = db.query(MoveCardModel.move_card_id).filter(MoveCardModel.match_id == match_id).all()
            move_card_ids = [mc[0] for mc in move_cards]

            if not move_cards:
                raise HTTPException(status_code=404, detail="No move cards found for this match")
            
            return move_card_ids
        finally:
            db.close()

    def get_move_cards_id_inactive_in_match(self, match_id: int):
        db = session()
        try:
            move_cards = db.query(MoveCardModel.move_card_id).filter(
                MoveCardModel.match_id == match_id,
                MoveCardModel.is_active == False
            ).all()
            move_card_ids = [mc[0] for mc in move_cards]

            if not move_cards:
                raise HTTPException(status_code=404, detail="No move cards found for this match")
            
            return move_card_ids
        finally:
            db.close()


    def assign_move_card_to_player(self, move_card_id: int, player_id: int):
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            move_card = db.get(MoveCardModel,move_card_id)

            if not move_card:
                raise HTTPException(status_code=404, detail="Move card not found")
            
            if move_card.is_active == True:
                raise HTTPException(status_code=400, detail="Move card is currently in use")

            if move_card.player_id:
                raise HTTPException(status_code=400, detail="Move card is already assigned to a player")
            
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            active_move_cards = db.query(MoveCardModel).filter(
                MoveCardModel.player_id == player_id,
                MoveCardModel.is_active == True
            ).count()            
            if isinstance(active_move_cards, int) and active_move_cards >= 3:
                raise HTTPException(status_code=400, detail="Player already has 3 active move cards")

            if move_card.match_id != player.match_id:
                raise HTTPException(status_code=400, detail="Move card does not belong to the player's match")
            
            move_card.player_id = player_id
            player.move_cards.append(move_card)
            move_card.is_active = True

            db.commit()

            return move_card
        finally:
            db.close()


    def get_move_cards_by_player(self, player_id: int) -> list[MoveCardModel]:
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            move_cards = db.query(MoveCardModel).filter(MoveCardModel.player_id == player_id).all()
            if not move_cards:
                raise HTTPException(status_code=404, detail="No move cards found for this player")
            
            return move_cards
        finally:
            db.close()
    
    def soft_move(self, player_id: int, move_card_id: int, movement_info: MoveCardIn, log = True): # fijarse si es el turno del jugador!!!
        player_cards = self.get_move_cards_by_player(player_id)
        move_card_ids = [card.move_card_id for card in player_cards]
        if move_card_id not in move_card_ids:
            raise HTTPException(status_code=404, detail="Move card not found for this player")
        
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            match = db.get(MatchModel,player.match_id)
            card = db.get(MoveCardModel,move_card_id)

            if not player or not match or not card:
                raise HTTPException(status_code=404, detail="Something not found")
            if player.matches.current_turn != player_id:
                raise HTTPException(status_code=400, detail="Not player's turn")

            # añadir carta a lista cartas usadas, crea la lista si no existe (modularizar?)
            
            if not player.used_cards:
                used_cards = []
            else:
                used_cards = json.loads(player.used_cards)
            if card.move_card_id in used_cards:
                raise HTTPException(status_code=400, detail="Move card already used")
            used_cards.append(card.move_card_id)

            # Valida input
            board = json.loads(match.board)
            if not movement_info.position or not movement_info.orientation:
                raise HTTPException(status_code=400, detail="Invalid movement info, missing fields")
            if movement_info.position[0] != "[" or movement_info.position[-1] != "]":
                raise HTTPException(status_code=400, detail="Invalid position format, the correct format is a string like this: '[x, y]'")
            
            if len(json.loads(movement_info.position)) != 2: # esta en esta linea intencionalmente. ):C
                raise HTTPException(status_code=400, detail="Invalid position format, the correct format is a string like this: '[x, y]'")
            
            # Valida movimiento
            self.__apply_move_card(card.move_card_type.value, board, movement_info.orientation, json.loads(movement_info.position))

            # actualizacion en database
            player.used_cards = json.dumps(used_cards)
            card.last_used_orientation = movement_info.orientation
            card.last_used_position = movement_info.position
            db.commit()
            
            # crear lista de cartas usadas (wtf este comentario? lo puse yo encima)
            board = json.loads(match.board)

            for i in range(len(used_cards)):
                used_card = db.get(MoveCardModel,used_cards[i])
                board = self.__apply_move_card(
                    used_card.move_card_type.value, 
                    board, used_card.last_used_orientation, 
                    json.loads(used_card.last_used_position)
                )
                



            # printing   
            print(f"The LAST card type is {used_card.move_card_type.name}, the orientation is {used_card.last_used_orientation} and the position is {json.loads(used_card.last_used_position)}\n")
            for cards in player.move_cards:
                if cards.move_card_id not in used_cards:
                    move_card_type_str = MoveCardRepository().imprimir_tipo_de_movimiento(cards.move_card_type.value).replace('\n', '')
                    print(f"{cards.move_card_id} - {move_card_type_str}")
            self.pretty_print_board(board)
        
    
            db.commit() # si el movimiento no es valido salta excepcion en apply_move_card

            print("\n" + "="*30)
            print("USING MOVE CARD HERE")
            print("="*30 + "\n")

            shapes = ShapeDetector().test_shape_fitting(board)
            shapes = {shape: shapes[shape] for shape in shapes if shapes[shape]['color'] != match.prohibited_color}
            ShapeDetector().pretty_print_result(shapes)

            # MESSAGE
            if log:
                player_ids = [player.player_id for player in match.players]

                player_repo = PlayerRepository()
                asyncio.create_task(player_repo.broadcast_message_to_id_list(content=f"{player.username} used a move card.", 
                                                                    message_type=messageType.PlayerUsesMoveCard, 
                                                                    match_id=match.match_id, 
                                                                  ids=player_ids))
            
            return board, shapes
        finally:
            db.close()
    
    def pretty_print_board(self, board: list[list[str]]):
        col_coords = "    " + "   ".join([str(i) for i in range(len(board[0]))])
        print(col_coords)
        
        row_separator = "  +" + "---+" * len(board[0])
        for idx, row in enumerate(board):
            print(row_separator)
            print(f"{idx} | " + " | ".join(row) + " |")
        print(row_separator)

    def confirm_moves(self, player_id: int):
        # usada en pass_turn, unassignea las cartas del jugador usadas
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            match = db.get(MatchModel,player.match_id)
            if not player or not match:
                raise HTTPException(status_code=404, detail="Something not found")
            
            board = json.loads(match.board)

            used_cards = json.loads(player.used_cards)
            if not used_cards or used_cards == []:
                shapes = ShapeDetector().test_shape_fitting(board)
                shapes = {shape: shapes[shape] for shape in shapes if shapes[shape]['color'] != match.prohibited_color}
                return board, shapes # regreso board sin tocar, y lista vacia 
            
            # MODULARIZAR ESTO POR DIOS
            
            self.pretty_print_board(board)
            
            
            for i in range(len(used_cards)):
                used_card = db.get(MoveCardModel,used_cards[i])
                board = self.__apply_move_card(
                    used_card.move_card_type.value, 
                    board, used_card.last_used_orientation, 
                    json.loads(used_card.last_used_position)
                )

                print(f"\n\n Iteracion {i}:\n")
                print(f"The card type is {used_card.move_card_type.value}, the orientation is {used_card.last_used_orientation} and the position is {json.loads(used_card.last_used_position)}\n")
                self.pretty_print_board(board)

            

            # ELIMINAR CARTAS USADAS
            for card_id in used_cards:
                card = db.get(MoveCardModel,card_id)
                card.is_active = False
                card.player_id = None
                if card in player.move_cards:
                    player.move_cards.remove(card)

            player.used_cards = json.dumps([])
            match.board = json.dumps(board)
            db.commit()

            shapes = ShapeDetector().test_shape_fitting(board)
            shapes = {shape: shapes[shape] for shape in shapes if shapes[shape]['color'] != match.prohibited_color}
            ShapeDetector().pretty_print_result(shapes)

            return board, shapes
        finally:
            db.close()
        

    def cancel_soft_move(self, player_id: int, log = True):
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            if not player.used_cards or json.loads(player.used_cards) == []:
                raise HTTPException(status_code=404, detail="No move cards used by this player")
            used_cards = json.loads(player.used_cards)

            # la ultima carta usada
            last_used_card_id = used_cards[-1]
            last_used_card = next(card for card in player.move_cards if card.move_card_id == last_used_card_id)
            last_used_card.last_used_orientation = None
            last_used_card.last_used_position = None
            #########################
            used_cards.pop()
            player.used_cards = json.dumps(used_cards)
            db.commit()

            board = json.loads(player.matches.board)
            

            for i in range(len(used_cards)):
                used_card = db.get(MoveCardModel,used_cards[i])
                board = self.__apply_move_card(
                    used_card.move_card_type.value, 
                    board, used_card.last_used_orientation, 
                    json.loads(used_card.last_used_position)
                )

            print(f"The last move (card {last_used_card.move_card_id}) was canceled")
            for cards in player.move_cards:
                if cards.move_card_id not in used_cards:
                    move_card_type_str = MoveCardRepository().imprimir_tipo_de_movimiento(cards.move_card_type.value).replace('\n', '')
                    print(f"{cards.move_card_id} - {move_card_type_str}")
            self.pretty_print_board(board)

            
            shapes = ShapeDetector().test_shape_fitting(board)
            shapes = {shape: shapes[shape] for shape in shapes if shapes[shape]['color'] != player.matches.prohibited_color}
            ShapeDetector().pretty_print_result(shapes)

            # MESSAGE
            if log:
                player_ids = [player.player_id for player in player.matches.players]

                player_repo = PlayerRepository()
                asyncio.create_task(player_repo.broadcast_message_to_id_list(content=f"{player.username} canceled a move.", 
                                                                    message_type=messageType.PlayerCancelMove, 
                                                                    match_id=player.matches.match_id, 
                                                                    ids=player_ids))

            return board, shapes
            
        finally:
            db.close()
        
    
    def __apply_move_card(self, move_type: int, board: list[list[str]], orientation: str, position: list[int]):
        movement = self.__get_card_movement(move_type, orientation)
        x = position[0]
        y = position[1]
        new_x = x + movement[0]
        new_y = y + movement[1]
        if 0 <= new_x < len(board) and 0 <= new_y < len(board[0]):
            board[x][y], board[new_x][new_y] = board[new_x][new_y], board[x][y]
        else:
            raise HTTPException(status_code=400, detail="Invalid move")
        return board

    def __get_card_movement(self, move_type: int, orientation: str) -> list[int]:
        # devuelve los numeros a sumar a las cordenadas del board
        if orientation not in ["up", "down", "left", "right"]:
            raise HTTPException(status_code=400, detail="Invalid orientation")
        
        movements = {
            2: { # Salto diagonal de una casilla
                "up": [-2, 2],
                "down": [2, -2],
                "left": [-2, -2],
                "right": [2, 2]
            },
            4: { # Salto recto de una casilla
                "up": [-2, 0],
                "down": [2, 0],
                "left": [0, -2],
                "right": [0, 2]
            },
            3: { # Recto sin saltar
                "up": [-1, 0],
                "down": [1, 0],
                "left": [0, -1],
                "right": [0, 1]
            },
            1: { # Diagonal sin saltar
                "up": [-1, 1],
                "down": [1, -1],
                "left": [-1, -1],
                "right": [1, 1]
            },
            6: { # L invertida
                "up": [-2, 1],
                "down": [2, -1],
                "left": [-1, -2],
                "right": [1, 2]
            },
            5: { # L
                "up": [-2, -1],
                "down": [2, 1],
                "left": [1, -2],
                "right": [-1, 2]
            },
            7: { # Salto recto de cuatro casillas
                "up": [-4, 0],
                "down": [4, 0],
                "left": [0, -4],
                "right": [0, 4]
            }
        }
        
        if move_type not in movements:
            raise HTTPException(status_code=400, detail="Invalid move type")
        
        return movements[move_type][orientation]
        
    def imprimir_tipo_de_movimiento(self, tipo_de_movimiento: int):
        movimientos = {
            1: "Diagonal sin saltar",
            2: "Salto diagonal de una casilla",
            3: "Recto sin saltar",
            4: "Salto recto de una casilla",
            5: "L",
            6: "L invertida",
            7: "Salto recto de cuatro casillas"
        }
        descripcion_movimiento = movimientos.get(tipo_de_movimiento, "Tipo de movimiento inválido")
        return f"Tipo: {descripcion_movimiento}"
    
    # futuro para terminar turno 
    def get_amount_of_move_cards_by_player(self, player_id: int) -> int:
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            move_card_count = db.query(MoveCardModel).filter(MoveCardModel.player_id == player_id).count()
            return move_card_count
        finally:
            db.close()

    def preview_move_card(self, movement_info: MoveCardPreview) -> dict:
        try:
            db = session()

            if movement_info.position[0] != "[" or movement_info.position[-1] != "]":
                raise HTTPException(status_code=400, detail="Invalid position format, the correct format is a string like this: '[x, y]'")
            
            res = {}
            board = \
            [
                ["", "", "", "", "", ""],
                ["", "", "", "", "", ""],
                ["", "", "", "", "", ""],
                ["", "", "", "", "", ""],
                ["", "", "", "", "", ""],
                ["", "", "", "", "", ""]
            ]
            position_list = json.loads(movement_info.position)
            if len(position_list) != 2:
                raise HTTPException(status_code=400, detail="Invalid position format, the correct format is a string like this: '[x, y]'")
            
            x = position_list[0]
            y = position_list[1]
            for orientation in ["up", "down", "left", "right"]:
                movement = self.__get_card_movement(movement_info.move_type, orientation)
                new_x = x + movement[0]
                new_y = y + movement[1]
                if 0 <= new_x < len(board) and 0 <= new_y < len(board[0]):
                    res[orientation] = (new_x, new_y)
                else:
                    res[orientation] = None

            return res
        finally:
            db.close()
