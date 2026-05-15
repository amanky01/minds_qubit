"""
Conversation models.

Conversations are stored in per-agent databases:
    mindsqubit_agent_<agent_id> → conversations collection

Each document contains the full message history for one chat session.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models.shared import PyObjectId


class Message(BaseModel):
    role: str          # 'user' | 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationBase(BaseModel):
    user_id: str       # str of ObjectId — links back to central users collection
    agent_id: str
    messages: List[Message] = Field(default_factory=list)
    # Auto-generated from the first user message for display in history list
    title: Optional[str] = None
    # Agent-specific extra data (e.g. blog post id, research topic)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationInDB(ConversationBase):
    """Shape of a document in the agent's conversations collection."""
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class Conversation(ConversationBase):
    """API-facing shape (id as string, datetimes serialised)."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
