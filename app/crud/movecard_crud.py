from app.models.match_models import MoveCard as MoveCardModel
from app.models.player_models import Player as PlayerModel
from fastapi import HTTPException
from app.database import session

class MatchRepository:
    def create_move_Card(self, move_card_type) -> MoveCardModel:
        move_card = MoveCardModel(move_card_type = move_card_type)
        try:
            db = session()
            db.add(move_card)
            db.commit()
            db.refresh(move_card)
            return move_card
        finally:
            db.close()


    def get_move_card(card_id: int) -> MoveCardModel:
        db = session()
        try:
            move_card = db.query(MoveCardModel).get(card_id)
            return move_card
        finally:
            db.close()


    def get_move_cards_by_player(player_id: int) -> list[MoveCardModel]:
        db = session()
        try:
            move_cards = db.query(MoveCardModel).filter(MoveCardModel.player_id == player_id).all()
            return move_cards
        finally:
            db.close()


    def assign_move_card_to_player(move_card_id: int, player_id: int) -> MoveCardModel:
        db = session()
        try:
            move_card = get_move_card(move_card_id)
            if not move_card:
                raise HTTPException(status_code=404, detail="Move card not found")

            if move_card.is_active:
                raise HTTPException(status_code=400, detail="Move card is currently in use")

            move_card.player_id = player_id
            move_card.is_active = True
            db.commit()
            db.refresh(move_card)
            return move_card
        finally:
            db.close()


    def unassign_move_card_from_player(card_id: int):
        db = session()
        try:
            move_card = get_move_card(db, card_id)
            if not move_card:
                raise HTTPException(status_code=404, detail="Move card not found")

            if not move_card.is_active:
                raise HTTPException(status_code=400, detail="Move card is not active and cannot be unassigned")

            move_card.player_id = None
            move_card.is_active = False
            db.commit()
            db.refresh(move_card)
            return move_card
        finally:
            db.close()