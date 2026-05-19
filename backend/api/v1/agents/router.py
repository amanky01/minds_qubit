"""
Agents API — aggregates catalog, chat, and per-agent integration routers.

Structure
─────────
api/v1/agents/
  catalog/          GET /agents, /categories, /{agent_id}
  chat/             POST /agents/{agent_id}/execute, GET .../conversations
  opportunityalert/ POST/PATCH /agents/opportunityalert/subscribe, ...
  integrations.py   registry of integration routers (extend when adding agents)
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends

from api.v1.agents.catalog import router as catalog_router
from api.v1.agents.catalog.handlers import list_agents
from api.v1.agents.chat import router as chat_router
from api.v1.agents.integrations import INTEGRATION_ROUTERS
from api.v1.agents.schemas.catalog import AgentResponse
from core.dependencies import UserContext, get_optional_current_user

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents_endpoint(
    category: Optional[str] = None,
    user: Optional[UserContext] = Depends(get_optional_current_user),
) -> List[AgentResponse]:
    return await list_agents(category=category, _user=user)


# Fixed-path agent APIs before /{agent_id} catalog routes
for integration_router in INTEGRATION_ROUTERS:
    router.include_router(integration_router)

router.include_router(catalog_router)
router.include_router(chat_router)
