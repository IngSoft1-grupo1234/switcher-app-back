from fastapi import HTTPException
from app.models.match_models import Match as MatchModel
from app.models.player_models import Player as PlayerModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.crud.movecard_crud import MoveCardRepository
from app.crud.shapecard_crud import ShapeCardRepository
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
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
        move_card_repo = MoveCardRepository()
        shape_card_repo = ShapeCardRepository()

        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")

            self.__validate_match_start(match)
            
            move_card_types = MoveCardType.__members__.values()

            for move_card_type in move_card_types:
                for _ in range(7):
                    move_card_repo.create_move_card(match_id=match.match_id, move_card_type=move_card_type)
                    
            move_cards = db.query(MoveCardModel.move_card_id).filter(
                MoveCardModel.match_id == match_id,
                MoveCardModel.is_active == False,
                MoveCardModel.player_id == None
            ).all()

            random.shuffle(move_cards)

            match_players = self.get_player_ids_in_match(match_id)
            
            for player in match_players:
                player_cards = move_cards[:3]
                move_cards = move_cards[3:]

                for card in player_cards:
                    move_card_repo.assign_move_card_to_player(card, player)
            
            shape_card_types = ShapeCardType.__members__.values()

            for shape_card_type in shape_card_types:
                for _ in range(2):
                    shape_card_repo.create_shape_card(shape_card_type=shape_card_type)

            easy_shape_cards = db.query(ShapeCardModel.shape_card_id).filter(
                ShapeCardModel.player_id == None,
                ShapeCardModel.shape_card_difficulty == ShapeCardDifficulty.EASY
            ).all()

            hard_shape_cards = db.query(ShapeCardModel.shape_card_id).filter(
                ShapeCardModel.player_id == None,
                ShapeCardModel.shape_card_difficulty == ShapeCardDifficulty.HARD
            ).all()

            random.shuffle(easy_shape_cards)
            random.shuffle(hard_shape_cards)

            if len(match_players) == 2:
                for player in match_players:
                    easy_player_cards = easy_shape_cards[:8]
                    easy_shape_cards = easy_shape_cards[8:]
                    hard_player_cards = hard_shape_cards[:18]
                    hard_shape_cards = hard_shape_cards[18:]

                    for card in easy_player_cards:
                        shape_card_repo.assign_shape_card_to_player(card, player)
                    
                    for card in hard_player_cards:
                        shape_card_repo.assign_shape_card_to_player(card, player)

            elif len(match_players) == 3:
                for player in match_players:
                    easy_player_cards = easy_shape_cards[:4]
                    easy_shape_cards = easy_shape_cards[4:]
                    hard_player_cards = hard_shape_cards[:12]
                    hard_shape_cards = hard_shape_cards[12:]

                    for card in easy_player_cards:
                        shape_card_repo.assign_shape_card_to_player(card, player)
                    
                    for card in hard_player_cards:
                        shape_card_repo.assign_shape_card_to_player(card, player)
            else :
                for player in match_players:
                    easy_player_cards = easy_shape_cards[:4]
                    easy_shape_cards = easy_shape_cards[4:]
                    hard_player_cards = hard_shape_cards[:9]
                    hard_shape_cards = hard_shape_cards[9:]

                    for card in easy_player_cards:
                        shape_card_repo.assign_shape_card_to_player(card, player)
                    
                    for card in hard_player_cards:
                        shape_card_repo.assign_shape_card_to_player(card, player)


            shuffled_turns = self.__shuffle_turns(match.players)
            match.turns = json.dumps(shuffled_turns)
            match.has_begun = True                     

            db.commit()
            return shuffled_turns
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

    def set_match_turn(self, match_id, turn):
        db = session()
        try:
            match = db.query(MatchModel).get(match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found.")
            match.current_turn = turn
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
    
