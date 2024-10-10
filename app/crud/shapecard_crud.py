from app.models.player_models import Player as PlayerModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.models.match_models import Match as MatchModel
from app.crud.player_crud import PlayerRepository
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
from app.database import session
from fastapi import HTTPException

class ShapeCardRepository:
    def create_shape_card(self, shape_card_type: ShapeCardType):
        db = session()
        try:
            try:
                shape_card_type = ShapeCardType(shape_card_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Shape card type does not exist")
            
            if shape_card_type.value <= 18:
                shape_card_difficulty = ShapeCardDifficulty.HARD
            else:
                shape_card_difficulty = ShapeCardDifficulty.EASY
            
            shape_card = ShapeCardModel(shape_card_type=shape_card_type, shape_card_difficulty=shape_card_difficulty)
            
            db.add(shape_card)
            db.commit()
            db.refresh(shape_card)
            return shape_card.shape_card_id
        finally:
            db.close()


    def assign_shape_card_to_player(self, shape_card_id: int, player_id: int) :
        db = session()
        try:
            player_repo = PlayerRepository()
            player = db.get(PlayerModel,player_id)
            shape_card = db.get(ShapeCardModel,shape_card_id)

            if not shape_card:
                raise HTTPException(status_code=404, detail="Shape card not found")

            if shape_card.player_id:
                raise HTTPException(status_code=400, detail="Shape card is already assigned to a player")
            
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            shape_card.player_id = player_id
            player.shape_cards.append(shape_card)

            db.commit()

            return shape_card
        finally:
            db.close()

    def set_active_shape_card(self, shape_card_id: int): # nueva!!!
        db = session()
        try:
            shape_card = db.get(ShapeCardModel,shape_card_id)
            if not shape_card:
                raise HTTPException(status_code=404, detail="Shape card not found")
            
            shape_card.is_active = True
            db.commit()
        finally:
            db.close()

    def get_shape_cards_by_player(self, player_id: int) -> list[ShapeCardModel]:
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            shape_cards = db.query(ShapeCardModel).filter(ShapeCardModel.player_id == player_id, 
                                                          ShapeCardModel.is_active == True).all()
            if not shape_cards:
                raise HTTPException(status_code=404, detail="No shape cards found for this player")
            
            return shape_cards
        finally:
            db.close()
    
    # futuro para terminar turno 
    # def get_amount_of_move_cards_by_player(self, player_id: int) -> int:
    #     db = session()
    #     try:
    #         player = db.get(PlayerModel,player_id)
    #         if not player:
    #             raise HTTPException(status_code=404, detail="Player not found")
            
    #         move_card_count = db.query(MoveCardModel).filter(MoveCardModel.player_id == player_id).count()
    #         return move_card_count
    #     finally:
    #         db.close()