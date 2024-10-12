from app.database import Base
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.orm import declarative_base
from enum import Enum

class MoveCardType(Enum):
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
    move_card_type = Column(SQLAEnum(MoveCardType), nullable=False)
    player_id = Column(Integer, ForeignKey('players.player_id'), nullable=True)
    match_id = Column(Integer, ForeignKey('matches.match_id'), nullable=False)
    last_used_orientation = Column(Text, nullable=True)
    last_used_position = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)


    players = relationship("Player", back_populates="move_cards")
    matches = relationship("Match", back_populates="move_cards")
    
