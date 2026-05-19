"""Shared helpers for agent API routers."""

from __future__ import annotations

from api.v1.agents.schemas.catalog import AgentResponse
from core.dependencies import UserContext
from services.agent_catalog import AgentDefinition
from services.quota_service import quota_service


def agent_to_response(agent: AgentDefinition) -> AgentResponse:
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        icon=agent.icon,
        category=agent.category,
        features=agent.features,
    )


async def check_agent_quota(user: UserContext, agent_id: str) -> None:
    await quota_service.check_quota(
        user_id=user["user_id"],
        agent_id=agent_id,
        plan_id=user["plan_id"],
    )
