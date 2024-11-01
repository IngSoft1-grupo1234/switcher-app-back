from app.database import Base
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.orm import declarative_base
from enum import Enum

class ShapeCardType(Enum):
    SHAPE1 = 1
    SHAPE2 = 2
    SHAPE3 = 3
    SHAPE4 = 4
    SHAPE5 = 5
    SHAPE6 = 6
    SHAPE7 = 7
    SHAPE8 = 8
    SHAPE9 = 9
    SHAPE10 = 10
    SHAPE11 = 11
    SHAPE12 = 12
    SHAPE13 = 13
    SHAPE14 = 14
    SHAPE15 = 15
    SHAPE16 = 16
    SHAPE17 = 17
    SHAPE18 = 18
    SHAPE19 = 19
    SHAPE20 = 20
    SHAPE21 = 21
    SHAPE22 = 22
    SHAPE23 = 23
    SHAPE24 = 24
    SHAPE25 = 25

class ShapeCardDifficulty(Enum):
    EASY = 1
    HARD = 2

class ShapeCard(Base):
    __tablename__ = "shape_cards"

    shape_card_id = Column(Integer, primary_key=True, autoincrement=True)
    shape_card_type = Column(SQLAEnum(ShapeCardType), nullable=False)
    shape_card_difficulty = Column(SQLAEnum(ShapeCardDifficulty), nullable=False)
    player_id = Column(Integer, ForeignKey('players.player_id'), nullable=True)
    is_active = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    players = relationship("Player", back_populates="shape_cards")
