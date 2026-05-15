"""
Agents API router.

Endpoints
─────────
GET  /agents                           list all agents (public)
GET  /agents/categories                list all categories (public)
GET  /agents/{agent_id}                get agent details (public)
POST /agents/{agent_id}/execute        chat with an agent (auth + quota)
GET  /agents/{agent_id}/conversations  conversation history (auth required)
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.agents.schemas import (
    AgentExecuteRequest,
    AgentExecuteResponse,
    AgentResponse,
    ConversationResponse,
)
from api.v1.agents.service import agent_service
from core.dependencies import UserContext, get_current_user, get_optional_current_user
from services.quota_service import quota_service

router = APIRouter(prefix="/agents", tags=["agents"])


# ── Public endpoints ───────────────────────────────────────────────────────

@router.get("", response_model=List[AgentResponse])
async def list_agents(
    category: Optional[str] = None,
    _user: Optional[UserContext] = Depends(get_optional_current_user),
) -> List[AgentResponse]:
    """Return all registered agents, optionally filtered by category."""
    agents = (
        await agent_service.get_agents_by_category(category)
        if category
        else await agent_service.get_all_agents()
    )
    return [_to_response(a) for a in agents]


@router.get("/categories", response_model=List[str])
async def get_categories() -> List[str]:
    """Return all distinct agent categories."""
    return await agent_service.get_all_categories()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Return details for a single agent."""
    agent = await agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found.",
        )
    return _to_response(agent)


# ── Protected endpoints ────────────────────────────────────────────────────

@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    user: UserContext = Depends(get_current_user),
) -> AgentExecuteResponse:
    """
    Send a message to an agent and receive a response.
    Requires a valid JWT.  Quota is checked before the agent runs.
    Returns HTTP 429 if the user's daily or monthly limit is exhausted.
    """
    # Quota check runs inline so agent_id from the path param is available
    await quota_service.check_quota(
        user_id=user["user_id"],
        agent_id=agent_id,
        plan_id=user["plan_id"],
    )

    try:
        result = await agent_service.execute_agent(
            agent_id=agent_id,
            user_message=request.message,
            user_id=user["user_id"],
            plan_id=user["plan_id"],
            conversation_id=request.conversation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return AgentExecuteResponse(
        response=result["response"],
        conversation_id=result["conversation_id"],
        agent_id=result["agent_id"],
    )


@router.get("/{agent_id}/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    agent_id: str,
    user: UserContext = Depends(get_current_user),
) -> List[ConversationResponse]:
    """Return the authenticated user's conversation history with this agent."""
    conversations = await agent_service.get_user_conversations(
        user_id=user["user_id"],
        agent_id=agent_id,
    )
    return [ConversationResponse(**conv) for conv in conversations]


# ── Helper ─────────────────────────────────────────────────────────────────

def _to_response(agent) -> AgentResponse:
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        icon=agent.icon,
        category=agent.category,
        features=agent.features,
    )


