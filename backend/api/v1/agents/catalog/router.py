"""Public catalog endpoints: list agents, categories, and agent details."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, status

from api.v1.agents.catalog.service import catalog_service
from api.v1.agents.common import agent_to_response
from api.v1.agents.schemas.catalog import AgentResponse

router = APIRouter()


@router.get("/categories", response_model=List[str])
async def get_categories() -> List[str]:
    """Return all distinct agent categories."""
    return await catalog_service.get_all_categories()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Return details for a single agent."""
    agent = await catalog_service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found.",
        )
    return agent_to_response(agent)
