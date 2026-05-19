from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AgentExecuteRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8_000)
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
    title: Optional[str] = None
    messages: List[ConversationMessage]
    created_at: str
    updated_at: str
