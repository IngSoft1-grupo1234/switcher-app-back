from fastapi import HTTPException
from app.models.match_models import Match as MatchModel
from app.models.player_models import Player as PlayerModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.crud.movecard_crud import MoveCardRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
from app.websocket.websocket_endpoints import player_manager
from app.models.chat_models import messageType
import asyncio
from app.crud.player_crud import PlayerRepository 
from app.database import session
from app.shape_detection.DFS import ShapeDetector
import random
import json
import asyncio
from datetime import datetime, timedelta

class MatchRepository:
    def __init__(self):
        # ESTO SE GUARDA EN TODOS LAS INSTANCIAS DE ESTA CLASE WUOOOOO UAUWAUAWUWAU
        if not hasattr(self.__class__, 'timer_events'):
            self.__class__.timer_events = {}
        if not hasattr(self.__class__, 'timer_tasks'):
            self.__class__.timer_tasks = {}

    def create_match(self, match_name, max_players, host, password) -> MatchModel:
        db_match = MatchModel(match_name=match_name, max_players=max_players, host=host, password=password)

        try:
            db = session()
            if db_match.password != "":
                db_match.isPrivate = True
            db.add(db_match)
            db.commit()
            db.refresh(db_match) # Consigue el ID que le dio la base de datos
            return db_match
        finally:
            db.close()
        
    def get_all_matches(self) -> dict:
        db = session()
        try:
            matches = db.query(MatchModel).all()
            match_list = [self.__match_to_dict(match) for match in matches]
            return {"matches": match_list}
        finally:
            db.close()

    def get_notbegun_matches(self) -> dict:
        db = session()
        try:
            unstarted_matches = db.query(MatchModel).filter(MatchModel.has_begun == False).all()
            match_list = match_list = [self.__match_to_dict(match) for match in unstarted_matches]
            return {"matches": match_list}
        finally:
            db.close()
    
    def get_match_dict(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            return self.__match_to_dict(match)
        finally:
            db.close()

    def get_match(self, match_id):
        db = session()
        try:
            match = db.get(MatchModel, match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            return match
        finally:
            db.close()
            
    def __match_to_dict(self, match) -> dict:
        return {
            "id": match.match_id,
            "match_name": match.match_name,
            "max_players": match.max_players,
            "host": match.host,
            "player_count": match.player_count,
            "current_turn": match.current_turn,
            "has_begun": match.has_begun,
            "players": [
                {
                    "player_id": player.player_id,
                    "username": player.username,
                }
                for player in match.players
            ],
            "turns": match.turns,
            "board": match.board,
            "isPrivate": match.isPrivate
        }

    def delete_match(self, match_id): # nunca usar esto, muerte instantanea
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            for player in match.players:
                player.match_id = None  # hay que usar unassing aqui
            db.delete(match)
            db.commit()

        finally:
            db.close()

    def start_match(self, match_id, log = True):
        db = session()
        move_card_repo = MoveCardRepository()
        shape_card_repo = ShapeCardRepository()

        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            if match.has_begun:
                raise HTTPException(status_code=409, detail="Match has already started.")

            self.__validate_match_start(match)
            # Distribuir cartas de movimiento
            
            self.__distribute_move_cards(match_id)
            delete_shape_cards = self.__distribute_shape_cards(match_id)
            
            for card in delete_shape_cards:
                delete_card = db.query(ShapeCardModel).get(card)
                db.delete(delete_card)
            
            shuffled_turns = self.__shuffle_turns(match.players)
            match.turns = json.dumps(shuffled_turns)
            match.has_begun = True
            match.current_turn = shuffled_turns[0]

            # Crea tablero y randomiza colores
            colors = ['r'] * 9 + ['b'] * 9 + ['y'] * 9 + ['g'] * 9
            random.shuffle(colors)
            board = [colors[i:i+6] for i in range(0, 36, 6)]
            match.board = json.dumps(board)

            # pretty print para testear jugar (comentar)
            player_cards = move_card_repo.get_move_cards_by_player(shuffled_turns[0])
            current_player = next(player for player in match.players if player.player_id == shuffled_turns[0])
            print(f"<THE TURN IS FOR THE PLAYER {shuffled_turns[0]}, KNOWN AS {current_player.username}>")
            print(f"THE PLAYER HAS THE FOLLOWING MOVE CARDS:")
            for cards in player_cards:
                move_card_type_str = move_card_repo.imprimir_tipo_de_movimiento(cards.move_card_type.value).replace('\n', '')
                print(f"{cards.move_card_id} - {move_card_type_str}")
            print(f"THE BOARD IS:\n")
            move_card_repo.pretty_print_board(board)
            
            ################################

            shapes = ShapeDetector().test_shape_fitting(board)
            ShapeDetector().pretty_print_result(shapes)

            db.commit()

            if log:
                player_ids = [player.player_id for player in match.players]

                player_repo = PlayerRepository()
                asyncio.create_task(player_repo.broadcast_message_to_id_list(content="The Host has started the game.", 
                                                                  message_type=messageType.PlayerStartsGame, 
                                                                  match_id=match.match_id, 
                                                                  ids=player_ids))
            
            # timer
            self.__start_timer(match_id)
            
            return {
                "turns": shuffled_turns,
                "board": board,
                "shapes": shapes
            }
        finally:
            db.close()

    # Modularizacion start_match, es privada
    def __validate_match_start(self, match):
        if match.player_count < 2:
            raise HTTPException(status_code=409, detail="Not enough players.")
        if match.player_count > match.max_players:
            raise HTTPException(status_code=409, detail="Match is full.")

    # Modularizacion start_match, es privada
    def __shuffle_turns(self, players):
        ids_list = [player.player_id for player in players]
        random.shuffle(ids_list)
        return ids_list
    
    # Modularization of start_match to distribute move cards, it is private
    def __distribute_move_cards(self, match_id):
        move_card_repo = MoveCardRepository()

        move_card_types = MoveCardType.__members__.values()

        for move_card_type in move_card_types:
            for _ in range(7):
                move_card_repo.create_move_card(match_id=match_id, move_card_type=move_card_type)
                    
        move_cards = move_card_repo.get_move_cards_id_in_match(match_id)
        random.shuffle(move_cards)

        match_players = self.get_player_ids_in_match(match_id)
        for player in match_players:
            player_cards = move_cards[:3]
            move_cards = move_cards[3:]

            for card in player_cards:
                move_card_repo.assign_move_card_to_player(card, player)
    
    # Modularization of start_match to distribute shape cards, it is private
    def __distribute_shape_cards(self, match_id):
        shape_card_repo = ShapeCardRepository()
        shape_card_types = ShapeCardType.__members__.values()

        for shape_card_type in shape_card_types:
            for _ in range(2):
                shape_card_repo.create_shape_card(shape_card_type)

        easy_shape_cards = shape_card_repo.get_easy_shape_cards_ids_unassigned()
        hard_shape_cards = shape_card_repo.get_hard_shape_cards_ids_unassigned()

        random.shuffle(easy_shape_cards)
        random.shuffle(hard_shape_cards)

        match_players = self.get_player_ids_in_match(match_id)
        
        easy_cards_per_player = len(easy_shape_cards) // len(match_players)
        hard_cards_per_player = len(hard_shape_cards) // len(match_players)

        for player in match_players:
            easy_player_cards = easy_shape_cards[:easy_cards_per_player]
            easy_shape_cards = easy_shape_cards[easy_cards_per_player:]
            hard_player_cards = hard_shape_cards[:hard_cards_per_player]
            hard_shape_cards = hard_shape_cards[hard_cards_per_player:]

            for card in easy_player_cards:
                shape_card_repo.assign_shape_card_to_player(card, player)
                    
            for card in hard_player_cards:
                shape_card_repo.assign_shape_card_to_player(card, player)

            all_shape_cards = hard_player_cards + easy_player_cards
            random.shuffle(all_shape_cards)
            active_shape_cards = all_shape_cards[:3]

            for card in active_shape_cards:
                shape_card_repo.set_active_shape_card(card)
        delete_shape_cards = easy_shape_cards + hard_shape_cards
        return delete_shape_cards




    def pass_turn(self, match_id, log = True, timercheck = True):
        db = session()
        move_card_repo = MoveCardRepository()
        try:
            match = db.query(MatchModel).get(match_id)
            
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            if not match.has_begun:
                raise HTTPException(status_code=409, detail="Match has not started.")
            
            player_turn = match.current_turn
            player = db.query(PlayerModel).get(player_turn)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            
            has_block_card = False
            for card in player.shape_cards:
                if card.is_blocked:
                    has_block_card = True
                    break
            
            if not has_block_card:
                # Assign shape cards to next player
                shape_card_repo = ShapeCardRepository()
                shape_card_amount = shape_card_repo.get_amount_of_shape_cards_by_player(player_turn)
                
                
                for _ in range(3 - shape_card_amount):
                    inactive_shapes = shape_card_repo.get_shape_cards_ids_inactive(player_turn)
                    if len(inactive_shapes) > 0:
                        shape_card_repo.set_active_shape_card(random.choice(inactive_shapes))

            # ERROR AQUI (? what)
            current_player = next(player for player in match.players if player.player_id == player_turn)
            
            
           
            board = json.loads(match.board)
            shapes = ShapeDetector().test_shape_fitting(board)
            used_cards = json.loads(current_player.used_cards)
            for _ in range(len(used_cards)):
                move_card_repo.cancel_soft_move(current_player.player_id)
            
            
            turns = json.loads(match.turns)
            current_index = turns.index(player_turn)
            next_index = (current_index + 1) % len(turns)
            next_turn = turns[next_index]

            match.current_turn = next_turn
            
            db.commit()

            if timercheck:
                if match_id not in self.timer_events or self.timer_events[match_id] is None:
                    if match_id not in self.timer_tasks or self.timer_tasks[match_id] is None:
                        self.__start_timer(match_id)

            if log:
                player_ids = [player.player_id for player in match.players]

                player_repo = PlayerRepository()
                asyncio.create_task(player_repo.broadcast_message_to_id_list(content=f"{current_player.username} has passed the turn.", 
                                                                  message_type=messageType.PlayerPassTurn, 
                                                                  match_id=current_player.match_id, 
                                                                  ids=player_ids))
            shapes = {shape: shapes[shape] for shape in shapes if shapes[shape]['color'] != match.prohibited_color}
            
            return board, shapes
        finally:
            db.close()

    
    # esto no se usa, chequear si se puede borrar :D
    def set_player_count(self, match_id, player_count):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            match.player_count = player_count
            db.commit()
        finally:
            db.close()

    def update_match(self, match_id, match_name=None, max_players=None, host=None):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if match:
                if match_name is not None:
                    match.match_name = match_name
                if max_players is not None:
                    match.max_players = max_players
                if host is not None:
                    match.host = host
                db.commit()
                db.refresh(match)
                return match
        finally:
            db.close()
    
    
    # Para obtener los IDs de los jugadores en una partida
    def get_player_ids_in_match(self, match_id):
        db = session()
        try:
            match = db.get(MatchModel, match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            elif match:
                player_ids = [player.player_id for player in match.players]
                return player_ids
        finally:
            db.close()
    

    # Para obtener el nombre del jugador que sigue en el turno
    def get_next_player(self, match_id):
        db = session()
        try:
            match = db.get(MatchModel, match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            if not match.has_begun:
                raise HTTPException(status_code=409, detail="Match has not started.")
            
            turns = json.loads(match.turns)
            current_index = turns.index(match.current_turn)
            next_index = (current_index + 1) % len(turns)
            next_player_id = turns[next_index]
            next_player = db.get(PlayerModel, next_player_id)
            if not next_player:
                raise HTTPException(status_code=404, detail="Next player not found.")
            return {
                "username": next_player.username,
                "player_id": next_player.player_id
            } if next_player else None
        finally:
            db.close()
    
    def get_turns(self, match_id):
        db = session()
        try:
            match = db.get(MatchModel, match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            turns = json.loads(match.turns)
            return turns
        finally:
            db.close()
    
    def get_board(self, match_id):
        db = session()
        try:
            match = db.get(MatchModel, match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            board = json.loads(match.board)
            return board
        finally:
            db.close()
    
    def __start_timer(self, match_id):
        print("""         .--.
    .-._;.--.;_.-.
   (_.'_..--.._'._)
    /.' . 120 . '.\\
   // .      / . \\\\
  |; .      /   . |;
  ||90    ()    30||
  |; .          . |;
   \\\\ .        . //
    \\'._' 60 '_.'/
     '-._'--'_.-'
         `""`  """)
        self.timer_events[match_id] = asyncio.Event()
        self.timer_tasks[match_id] = asyncio.create_task(self.timer(match_id))

    async def timer(self, match_id, log=True):
        while True:
            if match_id not in self.timer_events or self.timer_events[match_id] is None:
                break # Si la partida deja de existir...

            self.timer_events[match_id].clear()
            try:
                try:
                    await asyncio.wait_for(self.timer_events[match_id].wait(), timeout=1200)
                except asyncio.CancelledError:
                    break # Si la partida deja de existir...
            except asyncio.TimeoutError:
                # log de chat aqui
                if log:
                    asyncio.create_task(PlayerRepository.broadcast_message_to_id_list(
                        content="A MF was sleeping on the keyboard! The turn has been passed.",
                        message_type=messageType.PlayerPassTurn,
                        match_id=match_id, 
                        ids=self.get_player_ids_in_match(match_id)))
                    
                    
                try:
                    next_player_json = self.get_next_player(match_id=match_id) # error cuando solo queda un jugador y abandona?
                except HTTPException:
                    next_player_json = {"username": "ni en pedo me fijo en el username", "player_id": 999}
                
                if next_player_json:
                    message = {"action": "next-turn",
                                "data": {"next_player_name":next_player_json["username"],
                                        "next_player_id": next_player_json["player_id"]}
                            }
                    await player_manager.broadcast_to_id_list(json.dumps(message), self.get_player_ids_in_match(match_id))
                self.pass_turn(match_id)

    
        
      
    
    
