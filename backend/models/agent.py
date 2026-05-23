"""
Agent registry models.

The agent_registry collection in the central DB mirrors agent_catalog
metadata synced on core startup. Core does not access per-agent databases.
It exists so admin dashboards and future microservices can inspect
available agents without importing Python modules.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models.shared import PyObjectId


class AgentBase(BaseModel):
    id: str                        # e.g. 'codecraft'
    name: str
    description: str
    icon: str
    category: str
    features: List[str]
    agent_type: str = "chat"       # 'chat' | 'integration'
    service_url: str = ""
    is_remote: bool = True
    system_prompt: str = ""
    gemini_config: Dict[str, Any] = Field(default_factory=dict)
    # Quota defaults declared by the agent itself
    quota_config: Dict[str, int] = Field(default_factory=dict)
    is_live: bool = False


class AgentInDB(AgentBase):
    """Shape of a document in central DB → agent_registry collection."""
    mongo_id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class Agent(AgentBase):
    """API-facing shape."""
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
