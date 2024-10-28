from pydantic import BaseModel, Field, ConfigDict

class MoveCardIn (BaseModel):
    player_id: int
    model_config=ConfigDict(from_attributes=True)

class MoveCardOut (BaseModel): 
    player_id: int
    move_card_id : int
    move_card_type : int
    move_card_difficulty : int
    operation_result: str
    model_config=ConfigDict(from_attributes=True) # por que estan estas cosas aca xD

class UsedShapeSchema (BaseModel):
    color: str
    location: str
    model_config=ConfigDict(from_attributes=True)