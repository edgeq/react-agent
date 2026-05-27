from typing import Literal

from pydantic import BaseModel

class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None

class ConversationState(BaseModel):
    messages: list[Message] = []