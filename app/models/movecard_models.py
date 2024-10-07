import enum
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.orm import declarative_base

class MoveCardType(enum.Enum):
    MOV1 = 1
    MOV2 = 2
    MOV3 = 3
    MOV4 = 4
    MOV5 = 5
    MOV6 = 6
    MOV7 = 7

class MoveCard(Base):
    __tablename__ = "move_cards"

    move_card_id = Column(Integer, primary_key=True, autoincrement=True)
    move_card_type = Column(Enum(MoveCardType), nullable = False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    is_active = Column(Boolean, default=False)

    player = relationship("Player", back_populates="cards")
