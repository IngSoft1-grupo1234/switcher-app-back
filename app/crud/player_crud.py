from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
from app.crud.match_crud import MatchRepository
from app.database import session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

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

            # Si el jugador no esta en la partida
            if player.match_id != match.match_id:
                player.match_id = match.match_id
                match.players.append(player)
                if match.player_count is None: # cosa rara para test, no entiendo.
                    match.player_count = 0
                match.player_count += 1
                db.commit()
               
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
            match = db.get(MatchModel, player.match_id)
            if player.match_id is None:
                raise HTTPException(status_code=400, detail="Player is not assigned to any match.")
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            
            if match.has_begun: # desconectarse midgame, no pasa nada
                player.match_id = None
                match.player_count -= 1
                db.commit()
            elif match.host == player.player_id: # se desconecta el host en el lobby, se borra partida
                player.match_id = None
                db.delete(match)
                db.commit()
            else:
                player.match_id = None # se desconecta jugador en el lobby, no pasa nada
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
            if player.match:
                player.match.player_count -= 1
            db.delete(player)
            db.commit()
            return player
        finally:
            db.close()