from typing import Literal, Union
from pydantic import BaseModel

class TextMessage(BaseModel):
    role: Literal["developer", "user", "assistant"]
    content: str

class FunctionCallItem(BaseModel):
    type: Literal["function_call"] = "function_call"
    id: str
    call_id: str
    name: str
    arguments: str

class FunctionCallOutputItem(BaseModel):
    type: Literal["function_call_output"] = "function_call_output"
    call_id: str
    output: str

# A ConversationItem is any of the structured items that can be part of a Responses API conversation
ConversationItem = Union[TextMessage, FunctionCallItem, FunctionCallOutputItem]

class ConversationState(BaseModel):
    messages: list[ConversationItem] = []