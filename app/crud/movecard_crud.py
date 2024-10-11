from app.models.player_models import Player as PlayerModel
from app.models.movecard_models import MoveCard as MoveCardModel
from app.models.movecard_models import MoveCardType
from app.models.shapecard_models import ShapeCard as ShapeCardModel
from app.models.shapecard_models import ShapeCardType, ShapeCardDifficulty
from app.models.match_models import Match as MatchModel
from app.crud.player_crud import PlayerRepository
from app.database import session
from fastapi import HTTPException

class MoveCardRepository:
    def create_move_card(self, match_id: int, move_card_type: MoveCardType):
        db = session()
        try:
            try     :
                move_card_type = MoveCardType(move_card_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Move card type does not exist")
            
            move_card_count = db.query(MoveCardModel).filter(
                MoveCardModel.move_card_type == move_card_type,
                MoveCardModel.match_id == match_id
            ).count()
            if isinstance(move_card_count, int) and move_card_count >= 7:
                raise HTTPException(status_code=400, detail="Cannot create more than 7 move cards of the same type")
            
            move_card = MoveCardModel(match_id=match_id, move_card_type=move_card_type)
            db.add(move_card)
            db.commit()
            db.refresh(move_card)
            return move_card.move_card_id
        finally:
            db.close()
        
    def get_move_cards_id_in_match(self, match_id: int):
        db = session()
        try:
            move_cards = db.query(MoveCardModel.move_card_id).filter(MoveCardModel.match_id == match_id).all()
            move_card_ids = [mc[0] for mc in move_cards]

            if not move_cards:
                raise HTTPException(status_code=404, detail="No move cards found for this match")
            
            return move_card_ids
        finally:
            db.close()


    def assign_move_card_to_player(self, move_card_id: int, player_id: int):
        db = session()
        try:
            player_repo = PlayerRepository()
            player = db.get(PlayerModel,player_id)
            move_card = db.get(MoveCardModel,move_card_id)

            if not move_card:
                raise HTTPException(status_code=404, detail="Move card not found")
            
            if move_card.is_active == True:
                raise HTTPException(status_code=400, detail="Move card is currently in use")

            if move_card.player_id:
                raise HTTPException(status_code=400, detail="Move card is already assigned to a player")
            
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            active_move_cards = db.query(MoveCardModel).filter(
                MoveCardModel.player_id == player_id,
                MoveCardModel.is_active == True
            ).count()            
            if isinstance(active_move_cards, int) and active_move_cards >= 3:
                raise HTTPException(status_code=400, detail="Player already has 3 active move cards")

            if move_card.match_id != player.match_id:
                raise HTTPException(status_code=400, detail="Move card does not belong to the player's match")
            
            move_card.player_id = player_id
            player.move_cards.append(move_card)
            move_card.is_active = True

            db.commit()

            return move_card
        finally:
            db.close()


    def get_move_cards_by_player(self, player_id: int) -> list[MoveCardModel]:
        db = session()
        try:
            player = db.get(PlayerModel,player_id)
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            move_cards = db.query(MoveCardModel).filter(MoveCardModel.player_id == player_id).all()
            if not move_cards:
                raise HTTPException(status_code=404, detail="No move cards found for this player")
            
            return move_cards
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