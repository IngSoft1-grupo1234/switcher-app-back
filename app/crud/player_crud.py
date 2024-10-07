from app.models.player_models import Player as PlayerModel
from app.models.match_models import Match as MatchModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.database import session
from sqlalchemy.exc import IntegrityError


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
            player = db.query(PlayerModel).get(player_id)
            return player
        finally:
            db.close()
    
    def assign_match_to_player(self, player_id, match_id):
        try:
            db = session()
            player = db.get(PlayerModel, player_id)
            match = db.get(MatchModel, match_id)
            # abominacion
            if player:
                if match:
                    if player.match_id != match.match_id:
                        player.match_id = match.match_id
                        if match.player_count is None:
                            match.player_count = 0
                        match.players.append(player)
                        match.player_count += 1
                        db.commit()
                else:
                    return "Match not found"
            else: return "Player not found"
               
        except IntegrityError:
            return "limit reached"
        finally:
            db.close()
    
    def unassign_match_to_player(self, player_id):
        try:
            db = session()
            player = db.query(PlayerModel).get(player_id)
            if player:
                match = db.query(MatchModel).get(player.match_id)
                if match:
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
                else:
                    return "Player not belong to any match"
            else:
                return "Player not found"
        finally:
            db.close()
    
    def delete_player(self, player_id):
        try:
            db = session()
            player = db.query(PlayerModel).get(player_id)
            if player:
                if player.match:
                    player.match.player_count -= 1
                db.delete(player)
                db.commit()
            return player
        finally:
            db.close()