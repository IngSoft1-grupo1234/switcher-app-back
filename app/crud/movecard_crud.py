from app.models.player_models import Player as PlayerModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.database import session
from fastapi import HTTPException

class MoveCardRepository:
    def create_move_card(self, move_card_type) -> MoveCardModel:
        db = session()
        try:
            existing_move_card_type = db.query(MoveCardModel).filter(MoveCardModel.move_card_type == move_card_type).first()
            if not existing_move_card_type:
                raise HTTPException(status_code=400, detail="Move card type does not exist")
            
            move_card = MoveCardModel(move_card_type=move_card_type)
            db.add(move_card)
            db.commit()
            db.refresh(move_card)
            return move_card
        finally:
            db.close()


    def get_move_card(self, card_id: int) -> MoveCardModel:
        db = session()
        try:
            move_card = db.query(MoveCardModel).get(card_id)
            if not move_card:
                raise HTTPException(status_code=404, detail="Move card not found")
            return move_card
        finally:
            db.close()


    def get_move_cards_by_player(self, player_id: int) -> list[MoveCardModel]:
        db = session()
        try:
            player = db.query(PlayerModel).get(player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            move_cards = db.query(MoveCardModel).filter(MoveCardModel.player_id == player_id).all()
            return move_cards
        finally:
            db.close()


    def assign_move_card_to_player(self, move_card_id: int, player_id: int) -> MoveCardModel:
        db = session()
        try:
            move_card = self.get_move_card(move_card_id)
            if not move_card:
                raise HTTPException(status_code=404, detail="Move card not found")
            
            if move_card.is_active:
                raise HTTPException(status_code=400, detail="Move card is currently in use")

            player = db.query(PlayerModel).get(player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            active_move_cards = db.query(MoveCardModel).filter(
                MoveCardModel.player_id == player_id,
                MoveCardModel.is_active == True
            ).count()

            if isinstance(active_move_cards, int) and active_move_cards >= 3:
                raise HTTPException(status_code=400, detail="Player already has 3 active move cards")

            move_card.player_id = player_id
            move_card.is_active = True
            db.commit()
            db.refresh(move_card)
            return move_card
        finally:
            db.close()


    def unassign_move_card_from_player(self, card_id: int, player_id: int) -> MoveCardModel:
        db = session()
        try:
            move_card = self.get_move_card(card_id)
            if not move_card:
                raise HTTPException(status_code=404, detail="Move card not found")

            if not move_card.is_active:
                raise HTTPException(status_code=400, detail="Move card is not active and cannot be unassigned")
            
            player = db.query(PlayerModel).get(player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            if move_card.player_id != player_id:
                raise HTTPException(status_code=403, detail="Player does not own this move card")

            move_card.player_id = None
            move_card.is_active = False
            db.commit()
            db.refresh(move_card)
            return move_card
        finally:
            db.close()