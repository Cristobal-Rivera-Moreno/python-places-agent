from pydantic import BaseModel
from typing import List

class ChatMessage(BaseModel):
    role: str = 'user'
    content: str = ''

class ChatRequest(BaseModel):
    userId: str
    message: ChatMessage
    lat: float = 21.9167
    long: float = -102.3069
    chatHistory: list[ChatMessage]= []
