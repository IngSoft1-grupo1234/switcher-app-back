from pydantic import BaseModel

class PlayerIn(BaseModel):
    username: str

class PlayerOut(BaseModel):
    username: str
    player_id: int