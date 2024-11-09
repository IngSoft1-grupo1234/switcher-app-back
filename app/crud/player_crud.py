from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.movecard_models import MoveCard as MoveCardModel

from app.models.movecard_models import MoveCardType
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
from app.database import session
import random
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
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
    
    def assign_match_to_player(self, player_id, match_id):
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

            # Si el jugador no esta en la partida
            if player.match_id != match.match_id:
                player.match_id = match.match_id
                match.players.append(player)
                if match.player_count is None: # cosa rara para test, no entiendo.
                    match.player_count = 0
                match.player_count += 1
                db.commit()
            else:
                raise HTTPException(status_code=409, detail="Player is already in the match.")
               
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Match is full.")
        finally:
            db.close()
    
    def unassign_match_to_player(self, player_id):
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
                    winner_player.match_id = None


                    # borra el timer de la partida
                    from app.crud.match_crud import MatchRepository as MR
                    mr = MR()
                    if match.match_id in mr.timer_events and match.match_id in mr.timer_tasks:
                        del mr.timer_events[match.match_id]
                        del mr.timer_tasks[match.match_id]



                    db.delete(match)
                    db.commit()
                    return {"winner_username": winner_username, "winner_player_id": winner_player_id}
            # cancel match not started
            elif match.host == player.player_id:
                player.match_id = None
                db.delete(match)
            # disconnect player from match not started
            else:
                player.match_id = None
                match.player_count -= 1
            
            db.commit()
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
    
    def use_shape_card(self, shape_card_id, color, location):
        try:
            db = session()
            shape_card = db.get(ShapeCardModel, shape_card_id)
            if not shape_card:
                raise HTTPException(status_code=404, detail="Shape card not found.")
            if not shape_card.is_active:
                raise HTTPException(status_code=400, detail="Shape card is not active.")
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
            


            from app.crud.movecard_crud import MoveCardRepository
            move_card_repo = MoveCardRepository()
            move_card_repo.confirm_moves(match.current_turn)
            amount = move_card_repo.get_amount_of_move_cards_by_player(player.player_id)
            for _ in range(3 - amount):
                inactive_moves = move_card_repo.get_move_cards_id_inactive_in_match(match_id)
                if not inactive_moves:
                    raise HTTPException(status_code=400, detail="Match has no more move cards.")
                move_card_repo.assign_move_card_to_player(random.choice(inactive_moves), player.player_id)


            db.commit()

            return match.board, shapes
        finally:
            db.close()
    

    def winner_without_shape_card(self, player_id):
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
                for p in match.players:
                    shapes = db.query(ShapeCardModel).filter(ShapeCardModel.player_id == p.player_id).all()
                    for shape in shapes:
                        delete_shape = db.get(ShapeCardModel, shape.shape_card_id)
                        db.delete(delete_shape)
                    p.match_id = None
                
                # borra el timer de la partida
                from app.crud.match_crud import MatchRepository as MR
                mr = MR()
                if match.match_id in mr.timer_events and match.match_id in mr.timer_tasks:
                    del mr.timer_events[match.match_id]
                    del mr.timer_tasks[match.match_id]

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

    


        
