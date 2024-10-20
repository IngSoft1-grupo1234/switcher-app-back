from pydantic import BaseModel, Field, ConfigDict

class MoveCardIn (BaseModel):
    orientation: str
    position: str
    model_config=ConfigDict(from_attributes=True)

class MoveCardPreview (BaseModel):
    position: str
    move_type: int
    model_config=ConfigDict(from_attributes=True)
    
class MoveCardOut (BaseModel): 
    player_id: int
    move_card_id : int
    move_card_type : int
    operation_result: str
    model_config=ConfigDict(from_attributes=True)