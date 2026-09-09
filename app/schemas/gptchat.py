from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ChatMessage(BaseModel):
    user: str
    response: str
    timestamp: datetime


class ChatCreate(BaseModel):
    enr_no: str
    chats: list[ChatMessage]


class ChatResponse(BaseModel):
    id: int
    enr_no: str
    chats: list[ChatMessage]

    model_config = ConfigDict(from_attributes=True)