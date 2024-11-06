from pydantic import BaseModel, Field, ConfigDict

class MatchIn (BaseModel):
    match_name: str
    max_players: int = Field(..., ge=2, le=4)
    host: int
    password: str = ""
    model_config=ConfigDict(from_attributes=True)


class MatchOut (BaseModel): 
    match_name: str
    max_players: int
    host: int
    match_id: int
    operation_result: str
    model_config=ConfigDict(from_attributes=True)


