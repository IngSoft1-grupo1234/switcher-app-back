from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy import CheckConstraint
from app.database import Base
from sqlalchemy.orm import relationship

class Match(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, autoincrement=True)
    password = Column(String, nullable=False, default="")
    isPrivate = Column(Boolean, nullable=False, default=False)
    match_name = Column(String, nullable=False)
    max_players = Column(Integer, nullable=False)
    host = Column(Integer, nullable=False)
    player_count = Column(Integer, default=0)
    current_turn = Column(Integer, default=0)
    has_begun = Column(Boolean, default=False)
    turns = Column(Text, nullable=True, default="[]")
    board = Column(Text, nullable=True)
    prohibited_color = Column(Text, default="")
    players = relationship("Player", back_populates="matches")
    move_cards = relationship("MoveCard", back_populates="matches")
    chats = relationship("Chat", cascade="all, delete-orphan")
    

    __table_args__ = (
        CheckConstraint('player_count <= max_players', name='check_player_count_limit'),  # player_count must not exceed max_players
    )
