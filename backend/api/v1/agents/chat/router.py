"""Generic chat agent endpoints (all agents using execute + conversations)."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.agents.chat.service import chat_service
from api.v1.agents.common import check_agent_quota
from api.v1.agents.schemas.chat import (
    AgentExecuteRequest,
    AgentExecuteResponse,
    ConversationResponse,
)
from core.dependencies import UserContext, get_current_user

router = APIRouter()


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    user: UserContext = Depends(get_current_user),
) -> AgentExecuteResponse:
    """
    Send a message to an agent and receive a response.
    Requires a valid JWT. Quota is checked before the agent runs.
    """
    await check_agent_quota(user, agent_id)

    try:
        result = await chat_service.execute_agent(
            agent_id=agent_id,
            user_message=request.message,
            user_id=user["user_id"],
            user_email=user["email"],
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
    conversations = await chat_service.get_user_conversations(
        user_id=user["user_id"],
        user_email=user["email"],
        plan_id=user["plan_id"],
        agent_id=agent_id,
    )
    return [ConversationResponse(**conv) for conv in conversations]
