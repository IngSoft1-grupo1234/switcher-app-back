from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.orm import declarative_base

class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    match_id = Column(Integer, ForeignKey('matches.match_id'), nullable=True)

    matches = relationship("Match", back_populates="players")
    move_cards = relationship("MoveCard", back_populates="players")
    shape_cards = relationship("ShapeCard", back_populates="players")
    used_cards = Column(Text, nullable=True, default="[]") # ids de cartas usadas. sirve :)