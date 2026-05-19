from __future__ import annotations

from typing import List

from pydantic import BaseModel


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    category: str
    features: List[str]

    model_config = {"from_attributes": True}
