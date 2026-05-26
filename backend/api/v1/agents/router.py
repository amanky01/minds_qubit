"""
Agents API — catalog (public) + unified proxy to agent microservices.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends

from api.v1.agents.catalog import router as catalog_router
from api.v1.agents.catalog.handlers import list_agents
from api.v1.agents.opportunityalert.router import router as opportunityalert_router
from api.v1.agents.proxy import router as proxy_router
from api.v1.agents.schemas.catalog import AgentResponse
from core.dependencies import UserContext, get_optional_current_user

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents_endpoint(
    category: Optional[str] = None,
    user: Optional[UserContext] = Depends(get_optional_current_user),
) -> List[AgentResponse]:
    return await list_agents(category=category, _user=user)


router.include_router(opportunityalert_router)
router.include_router(proxy_router)
router.include_router(catalog_router)
