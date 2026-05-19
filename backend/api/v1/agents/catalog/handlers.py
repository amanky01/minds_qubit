"""Catalog route handlers (mounted from the parent agents router)."""

from __future__ import annotations

from typing import List, Optional

from api.v1.agents.catalog.service import catalog_service
from api.v1.agents.common import agent_to_response
from api.v1.agents.schemas.catalog import AgentResponse
from core.dependencies import UserContext


async def list_agents(
    category: Optional[str] = None,
    _user: Optional[UserContext] = None,
) -> List[AgentResponse]:
    """Return all registered agents, optionally filtered by category."""
    agents = (
        await catalog_service.get_agents_by_category(category)
        if category
        else await catalog_service.get_all_agents()
    )
    return [agent_to_response(a) for a in agents]
