from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    messages: List[Message]
    context: Optional[Dict[str, Any]] = None
    session_state: Optional[Any] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[Dict[str, Any]] = None
    session_state: Optional[Any] = None
