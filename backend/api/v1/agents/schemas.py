from pydantic import BaseModel
from typing import List, Optional


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    category: str
    features: List[str]
    
    class Config:
        from_attributes = True


class AgentExecuteRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class AgentExecuteResponse(BaseModel):
    response: str
    conversation_id: str
    agent_id: str


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    agent_id: str
    messages: List[ConversationMessage]
    created_at: str
    updated_at: str
