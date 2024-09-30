from app.models.match_models import Match as MatchModel
from app.models.player_models import Player as PlayerModel
from app.database import session

class MatchRepository:
    def create_match(self, match_name, max_players, host) -> MatchModel:
        db_match = MatchModel(match_name=match_name, max_players=max_players, host=host)

        try:
            db = session()
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
            match_list = [
                {
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
                    ]
                }
                for match in matches
            ]
            return {"matches": match_list}
        finally:
            db.close()

    def get_notbegun_matches(self) -> dict:
        db = session()
        try:
            unstarted_matches = db.query(MatchModel).filter(MatchModel.has_begun == False).all()
            match_list = [
                {
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
                    ]
                }
                for match in unstarted_matches
            ]
            return {"matches": match_list}
        finally:
            db.close()
    
    def get_match(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if match:
                match_dict = {
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
                    ]
                }
                return match_dict
        finally:
            db.close()

    def delete_match(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if match:
                for player in match.players:
                    player.match_id = None 
                db.delete(match)
                db.commit()
            return match
        finally:
            db.close()

    def start_match(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if match:
                if match.player_count < 2:
                    return "not enough players"
                else:
                    match.has_begun = True
                    db.commit()
                    return "started"
        finally:
            db.close()

    def set_match_turn(self, match_id, turn):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if match:
                match.current_turn = turn
                db.commit()
                return match
        finally:
            db.close()
    
    def set_player_count(self, match_id, player_count):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if match:
                match.player_count = player_count
                db.commit()
            return match
        finally:
            db.close()