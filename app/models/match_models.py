from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import CheckConstraint
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, autoincrement=True)
    match_name = Column(String, nullable=False)
    max_players = Column(Integer, nullable=False)
    host = Column(Integer, nullable=False)
    player_count = Column(Integer, default=0)
    current_turn = Column(Integer, default=1)
    has_begun = Column(Boolean, default=False)

    players = relationship("Player", back_populates="match")

    __table_args__ = (
        CheckConstraint('player_count <= max_players', name='check_player_count_limit'),  # player_count must not exceed max_players
    )