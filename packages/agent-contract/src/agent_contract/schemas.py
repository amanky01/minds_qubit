from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class ExecuteRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8_000)
    conversation_id: Optional[str] = None


class ExecuteResponse(BaseModel):
    response: str
    conversation_id: str
    agent_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationMessageOut(BaseModel):
    role: str
    content: str
    timestamp: str


class ConversationListItem(BaseModel):
    id: str
    user_id: str
    agent_id: str
    title: Optional[str] = None
    messages: List[ConversationMessageOut]
    created_at: str
    updated_at: str


class SubscribeRequest(BaseModel):
    email: EmailStr
    notification_categories: List[str] = Field(..., min_length=1)
    opportunity_types: List[str] = Field(..., min_length=1)


class SubscribeResponse(BaseModel):
    email: str
    status: str
    subscriber: Dict[str, Any]


class UnsubscribeRequest(BaseModel):
    email: EmailStr
