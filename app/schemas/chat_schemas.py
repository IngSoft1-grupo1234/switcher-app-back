from pydantic import BaseModel, ConfigDict

class ChatIn (BaseModel):
    content: str
    time: str
    model_config=ConfigDict(from_attributes=True)