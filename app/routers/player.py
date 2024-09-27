from fastapi import APIRouter, status
from pydantic import BaseModel

PLAYERS = []

router = APIRouter(tags=["players"])

class PlayerIn(BaseModel):
    username: str

class PlayerOut(BaseModel):
    playername: str
    playerId: int

# create a player
@router.post("/players/", response_model=PlayerOut,status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerIn) -> PlayerOut:
    playerId = len(PLAYERS)
    playername = player.username
    new_player = PlayerOut(playername= playername, playerId= playerId)
    PLAYERS.append(new_player)
    return new_player