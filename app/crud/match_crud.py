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
                    ],
                    "turns" : match.turns
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
                    ],
                    "turns" : match.turns
                }
                return match_dict
        finally:
            db.close()

    def delete_match(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            for player in match.players:
                player.match_id = None 
            db.delete(match)
            db.commit()

        finally:
            db.close()

    def start_match(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            
            self.__validate_match_start(match)
                
            # Crea turnos para jugadores
            shuffled_turns = self.__shuffle_turns(match.players)
            match.turns = json.dumps(shuffled_turns)
            match.has_begun = True
            match.current_turn = shuffled_turns[0]

            db.commit()
            return shuffled_turns # regresa lista normal para dumpearla despues
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


    def pass_turn(self, match_id):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)

            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            if not match.has_begun:
                raise HTTPException(status_code=409, detail="Match has not started.")
            
            turns = json.loads(match.turns)
            
            current_index = turns.index(match.current_turn)
            next_index = (current_index + 1) % len(turns)
            next_turn = turns[next_index]

            match.current_turn = next_turn
            db.commit()
        finally:
            db.close()

    
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
            return next_player.username if next_player else None
        finally:
            db.close()
    
        
      
    
    
