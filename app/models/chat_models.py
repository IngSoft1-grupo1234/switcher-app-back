from sqlalchemy import Column, Integer, Text, ForeignKey
from app.database import Base
from enum import Enum
from sqlalchemy import Enum as SQLAEnum

class messageType(Enum):
    PlayerMessage = 1
    PlayerUsesMoveCard = 2
    PlayerUsesShapeCard = 3
    PlayerCancelMove = 4
    PlayerPassTurn = 5
    PlayerWins = 6
    PlayerTimerRunsOut = 7
    PlayerDisconnects = 8
    PlayerJoins = 9
    PlayerStartsGame = 10

    def to_dict(self):
        return self.name


class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True, autoincrement=True)
    message_type = Column(SQLAEnum(messageType), nullable=False)
    content = Column(Text, nullable=True, default="")
    match_id = Column(Integer, ForeignKey('matches.match_id'), nullable=False)
    time_sent = Column(Text, nullable=False, default="")