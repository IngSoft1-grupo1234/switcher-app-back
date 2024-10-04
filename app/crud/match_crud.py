from fastapi import HTTPException
from app.models.match_models import Match as MatchModel
from app.models.player_models import Player as PlayerModel
from app.database import session
import random
import json

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
                # Setea has_begun si es posible
                if match.player_count < 2:
                    raise HTTPException(status_code=409, detail="Not enough players.")
                elif match.player_count > match.max_players:
                    raise HTTPException(status_code=409, detail="Match is full.")
                else:
                    match.has_begun = True
                    
                # Crea turnos para jugadores
                shuffled_turns = [player.player_id for player in match.players]
                random.shuffle(shuffled_turns)
                match.turns = json.dumps(shuffled_turns)
                db.commit()
                return shuffled_turns
            else:
                raise HTTPException(status_code=404, detail="Match not found.")
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
    
    def get_player_ids_in_match(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            elif match:
                player_ids = [player.player_id for player in match.players]
                return player_ids
        finally:
            db.close()
    
