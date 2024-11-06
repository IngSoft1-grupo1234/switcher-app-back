from pydantic import BaseModel, ConfigDict

class PlayerIn(BaseModel):
    username: str
    model_config=ConfigDict(from_attributes=True)

class PlayerOut(BaseModel):
    username: str
    player_id: int
    operation_result: str
    model_config=ConfigDict(from_attributes=True)

class Password(BaseModel):
    password: str
    model_config=ConfigDict(from_attributes=True)

class LogIn(BaseModel):
    log: bool