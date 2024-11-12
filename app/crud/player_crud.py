from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.movecard_models import MoveCard as MoveCardModel

from app.models.movecard_models import MoveCardType
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty # redundante 
from app.models.chat_models import Chat as ChatModel
from app.models.chat_models import messageType
from app.websocket.websocket_endpoints import player_manager
from app.database import session
import random
import asyncio
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import datetime
import json
from app.shape_detection.DFS import ShapeDetector

class PlayerRepository:
    def create_player(self, username) -> PlayerModel:
        db_player = PlayerModel(username=username)

        try:
            db = session()
            db.add(db_player)
            db.commit()
            db.refresh(db_player)
            return db_player
        finally:
            db.close()

    def get_player(self, player_id) -> PlayerModel:
        db = session()
        try:
            player = db.get(PlayerModel, player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            return player
        finally:
            db.close()
    
    def assign_match_to_player(self, player_id, match_id, password="", log = True):
        try:
            db = session()
            player = db.get(PlayerModel, player_id)
            match = db.get(MatchModel, match_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            if match.has_begun:
                raise HTTPException(status_code=400, detail="Match has already begun.")

            # password simple viste
            if match.password != password:
                raise HTTPException(status_code=401, detail="Incorrect password.")
            # Si el jugador no esta en la partida
            if player.match_id != match.match_id:
                player.match_id = match.match_id
                match.players.append(player) # al pedo
                if match.player_count is None: # cosa rara para test, no entiendo.
                    match.player_count = 0
                match.player_count += 1

                db.commit()

                # CHAT MESSAGE
                if log:
                    player_ids = [player.player_id for player in match.players]
                    asyncio.create_task(self.broadcast_message_to_id_list(content=f"{player.username} has joined the game.",
                                                                        message_type=messageType.PlayerJoins, 
                                                                        match_id=player.match_id, 
                                                                        ids=player_ids))
            else:
                raise HTTPException(status_code=409, detail="Player is already in the match.")
            

               
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Match is full.")
        finally:
            db.close()
    
    def unassign_match_to_player(self, player_id, log = True): # si abandona jugador actual_turn se caga todo creo
        try:
            db = session()
            player = db.get(PlayerModel, player_id)

            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            if player.match_id is None:
                raise HTTPException(status_code=400, detail="Player is not assigned to any match.")
            match = db.get(MatchModel, player.match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            # unassign player from match already started
            if match.has_begun:

                # update match's turns 
                turns = json.loads(match.turns)
                if not player_id in turns:
                    raise HTTPException(status_code=400, detail="Player is not in turns.")    
                turns.remove(player_id)
                match.turns = json.dumps(turns)
                # update match's moves
                moves = db.query(MoveCardModel).filter(MoveCardModel.player_id == player.player_id).all()
                if not moves:
                    raise HTTPException(status_code=400, detail="Player has no moves.")
                for move in moves:
                    move.is_active = False
                    move.player_id = None
                    move.last_used_orientation = None
                    move.last_used_position = None
                # update match's shapes
                shapes = db.query(ShapeCardModel).filter(ShapeCardModel.player_id == player.player_id).all()
                if not shapes:
                    raise HTTPException(status_code=400, detail="Player has no shapes.")
                for shape in shapes:
                    delete_shape = db.get(ShapeCardModel, shape.shape_card_id)
                    db.delete(delete_shape)
                player.match_id = None
                player.move_cards = []
                player.shape_cards = []
                
                # clean up match's attributes
                match.player_count -= 1
                # check if player is the winner
                if match.player_count == 1:
                    winner_player = self.get_player(match.players[0].player_id)
                    winner_username = winner_player.username
                    winner_player_id = winner_player.player_id

                    # remove all moves from match
                    moves = db.query(MoveCardModel).filter(MoveCardModel.match_id == match.match_id).all()
                    if not moves:
                        raise HTTPException(status_code=400, detail="Player has no moves.")
                    for move in moves:
                        delete_move = db.get(MoveCardModel, move.move_card_id)
                        db.delete(delete_move)
                    # remove all shapes from player
                    shapes = db.query(ShapeCardModel).filter(ShapeCardModel.player_id == winner_player.player_id).all()
                    if not shapes:
                        raise HTTPException(status_code=400, detail="Player has no shapes.")
                    for shape in shapes:
                        delete_shape = db.get(ShapeCardModel, shape.shape_card_id)
                        db.delete(delete_shape)
                    # remove all chat messages from match
                    for chat in match.chats:
                        delete_chat = db.get(ChatModel, chat.chat_id)
                        db.delete(delete_chat)
                    winner_player.match_id = None
                    db.delete(match)
                    db.commit()
                    return {"winner_username": winner_username, "winner_player_id": winner_player_id}
            # cancel match not started
            elif match.host == player.player_id:
                player.match_id = None
                for chat in match.chats:
                    delete_chat = db.get(ChatModel, chat.chat_id)
                    db.delete(delete_chat)
                db.delete(match)
            # disconnect player from match not started
            else:
                player.match_id = None
                match.player_count -= 1
            
            db.commit()

            # CHAT MESSAGE
            if log: 
                player_ids = [player.player_id for player in match.players]
                if match:
                    asyncio.create_task(self.broadcast_message_to_id_list(content=f"{player.username} has left the game.",
                                                                      message_type=messageType.PlayerDisconnects, 
                                                                      match_id=match.match_id, 
                                                                      ids=player_ids))
        finally:
            db.close()
    
    def delete_player(self, player_id):
        try:
            db = session()
            player = db.get(PlayerModel, player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            if player.matches:
                self.unassign_match_to_player(player_id)
            db.delete(player)
            db.commit()
        finally:
            db.close()
    
    def use_shape_card(self, shape_card_id, color, location, log = True):
        try:
            db = session()
            shape_card = db.get(ShapeCardModel, shape_card_id)
            if not shape_card:
                raise HTTPException(status_code=404, detail="Shape card not found.")
            if not shape_card.is_active:
                raise HTTPException(status_code=400, detail="Shape card is not active.")
            if shape_card.is_blocked:
                raise HTTPException(status_code=400, detail="Shape card is blocked.")
            player = db.get(PlayerModel, shape_card.player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            if player.player_id != shape_card.player_id:
                raise HTTPException(status_code=400, detail="Shape card is not assigned to the player.")
            
            match_id = player.match_id
            match = db.get(MatchModel, match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            if player.player_id != match.current_turn:
                raise HTTPException(status_code=400, detail="It is not your turn.")
            
            


            if  color == match.prohibited_color: # si location esta dentro de alguna figura prohibida
                raise HTTPException(status_code=400, detail="Color is prohibited.")

            shapes = ShapeDetector().test_shape_fitting(json.loads(match.board))
            match.prohibited_color = color
            shapes = {shape: shapes[shape] for shape in shapes if shapes[shape]['color'] != color}
            
            shape_card.is_active = False
            shape_card.player_id = None
            db.delete(shape_card)
            


            # Unblock shape card if it is possible
            amount_active_shape_cards = 0
            has_block_card = False

            for card in player.shape_cards:
                if card.is_active:
                    amount_active_shape_cards += 1
                if card.is_blocked:
                    has_block_card = True
                    block_card = card

            if amount_active_shape_cards == 1 and has_block_card:
                block_card.is_blocked = False
                message = {"action": "shape-card-unblock","data": {     "unblocked_shape_card_id": block_card.shape_card_id, 
                                                                        "unblocked_shape_card_type": block_card.shape_card_type.value, 
                                                                        "player_id": player.player_id, 
                                                                    }}
                print(f"SHAPE CARD UNBLOCKED MESSAGE: {message}")
                asyncio.create_task(player_manager.broadcast(json.dumps(message)))

            from app.crud.movecard_crud import MoveCardRepository
            move_card_repo = MoveCardRepository()
            turn = match.current_turn
            db.commit()

            move_card_repo.confirm_moves(turn)
            amount = move_card_repo.get_amount_of_move_cards_by_player(player.player_id)
            for _ in range(3 - amount):
                inactive_moves = move_card_repo.get_move_cards_id_inactive_in_match(match_id)
                if not inactive_moves:
                    raise HTTPException(status_code=400, detail="Match has no more move cards.")
                move_card_repo.assign_move_card_to_player(random.choice(inactive_moves), player.player_id)


            # CHAT MESSAGE
            if log:
                player_ids = [player.player_id for player in match.players]
                asyncio.create_task(self.broadcast_message_to_id_list(content=f"{player.username} has used a shape card.",
                                                                    message_type=messageType.PlayerUsesShapeCard, 
                                                                    match_id=player.match_id, 
                                                                    ids=player_ids))
                
            return match.board, shapes, match.prohibited_color

            
        finally:
            db.close()
    
    
    def winner_without_shape_card(self, player_id, log = True):
        db = session()
        try:
            player = db.get(PlayerModel, player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
        
            shape_cards = player.shape_cards

            # check if player has shape cards and is the winner
            if not shape_cards:
                match = db.get(MatchModel, player.match_id)

                winner_username = player.username
                winner_player_id = player.player_id

                # remove all moves from match
                moves = db.query(MoveCardModel).filter(MoveCardModel.match_id == match.match_id).all()
                if not moves:
                    raise HTTPException(status_code=400, detail="Player has no moves.")
                for move in moves:
                    delete_move = db.get(MoveCardModel, move.move_card_id)
                    db.delete(delete_move)

                # remove all shapes from player
                player_ids = [player.player_id for player in match.players]
                for p in match.players:
                    shapes = db.query(ShapeCardModel).filter(ShapeCardModel.player_id == p.player_id).all()
                    for shape in shapes:
                        delete_shape = db.get(ShapeCardModel, shape.shape_card_id)
                        db.delete(delete_shape)
                    p.match_id = None
                
                # remove all chat messages from match
                for chat in match.chats:
                    delete_chat = db.get(ChatModel, chat.chat_id)
                    db.delete(delete_chat)
                
                db.delete(match)
                db.commit()
                
                return {"winner_username": winner_username, "winner_player_id": winner_player_id}
        finally:
            db.close()
        
    
    def is_player_turn(self,player_id) :
        db = session()
        try:
            player = db.get(PlayerModel, player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            match = db.get(MatchModel, player.match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            turns = json.loads(match.turns)
            if len(turns) == 0:
                return "bazinga"
            return player.player_id == turns[0]
        finally:
            db.close()
        
    def block_shape_card(self, shape_card_id, color):
        try:
            db = session()
            shape_card = db.get(ShapeCardModel, shape_card_id)
            if not shape_card:
                raise HTTPException(status_code=404, detail="Shape card not found.")
            if not shape_card.is_active:
                raise HTTPException(status_code=400, detail="Shape card is not active.")
            player_block = db.get(PlayerModel, shape_card.player_id)
            if not player_block:
                raise HTTPException(status_code=404, detail="Player not found.")
            
            match_id = player_block.match_id
            match = db.get(MatchModel, match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")

            
            amount_shape_cards = 0
            for cards in player_block.shape_cards:
                if cards.is_active:
                    amount_shape_cards += 1
            
            if amount_shape_cards != 3:
                raise HTTPException(status_code=400, detail="Player does not have 3 active shape cards.")
            
            has_block_card = False
            for cards in player_block.shape_cards:
                if cards.is_blocked:
                    has_block_card = True
                    break
            if has_block_card:
                raise HTTPException(status_code=400, detail="Player already has a blocked shape card.")                

            shape_card.is_blocked = True

            player_turn = db.get(PlayerModel, match.current_turn)
            if not player_turn:
                raise HTTPException(status_code=404, detail="Player not found.")

            match.prohibited_color = color
            
            db.commit()

            from app.crud.movecard_crud import MoveCardRepository
            move_card_repo = MoveCardRepository()
            move_card_repo.confirm_moves(match.current_turn)
            amount = move_card_repo.get_amount_of_move_cards_by_player(player_turn.player_id)
            for _ in range(3 - amount):
                inactive_moves = move_card_repo.get_move_cards_id_inactive_in_match(match_id)
                if not inactive_moves:
                    raise HTTPException(status_code=400, detail="Match has no more move cards.")
                move_card_repo.assign_move_card_to_player(random.choice(inactive_moves), player_turn.player_id)


            return player_turn.player_id, color
        finally:
            db.close()

    def player_send_message(self, player_id, content, log = True):
        try:
            db = session()

            player = db.get(PlayerModel, player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found.")
            if player.match_id is None:
                raise HTTPException(status_code=400, detail="Player is not assigned to any match.")
            
            match = db.get(MatchModel, player.match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")

            player_ids = [player.player_id for player in match.players]

            content = f"{player.username}: {content}"

            if log:
                asyncio.create_task(self.broadcast_message_to_id_list(content=content, 
                                                message_type=messageType.PlayerMessage,
                                                match_id=player.match_id, 
                                                ids=player_ids))
            
        finally:
            db.close()

        
    async def broadcast_message_to_id_list(self, content: str, message_type: messageType, match_id: int, ids: list[int]):
        time = datetime.now().strftime("%H:%M")
        chat = ChatModel(message_type=message_type, 
                                 content=content,  
                                 match_id=match_id, 
                                 time_sent=time)
        
        try:
            db = session()
            db.add(chat)
            db.commit()
        finally:
            db.close()

        data_to_send = {
            "message_type": message_type.name,
            "content": content,
            "time_sent": time
        }
        
        message = {"action": "chat-message","data": {"message": data_to_send}}
        print(f"CHAT MESSAGE: {message}")
        await player_manager.broadcast_to_id_list(json.dumps(message), ids)


    


        
