from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    match_id = Column(Integer, ForeignKey('matches.match_id'), nullable=True)

    match = relationship("Match", back_populates="players")