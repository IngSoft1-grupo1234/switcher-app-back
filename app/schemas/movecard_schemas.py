from pydantic import BaseModel, Field, ConfigDict

class MovementIn (BaseModel):
    player_id: int
    model_config=ConfigDict(from_attributes=True)

class MovementOut (BaseModel): 
    player_id: int
    move_cards_id : int
    move_cards_type : int
    operation_result: str
    model_config=ConfigDict(from_attributes=True)