"""
OpportunityAlert subscription routes (backward-compatible).

Production frontends call:
  POST   /api/v1/agents/opportunityalert/subscribe
  PATCH  /api/v1/agents/opportunityalert/subscribe
  POST   /api/v1/agents/opportunityalert/unsubscribe

New clients may also use the generic proxy:
  POST /api/v1/agents/opportunityalert/proxy/v1/subscribe
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.agents.common import check_agent_quota
from api.v1.agents.opportunityalert.schemas import (
    OpportunitySubscribeRequest,
    OpportunitySubscribeResponse,
    OpportunityUnsubscribeRequest,
)
from core.dependencies import UserContext, get_current_user
from services.agent_catalog import get_agent
from services.agent_gateway import agent_gateway
from services.quota_service import quota_service

router = APIRouter(prefix="/opportunityalert", tags=["opportunityalert"])

AGENT_ID = "opportunityalert"


def _require_live_agent() -> None:
    agent = get_agent(AGENT_ID)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{AGENT_ID}' not found.",
        )
    if not agent.is_live:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent is not available yet",
        )


@router.post("/subscribe", response_model=OpportunitySubscribeResponse)
async def subscribe(
    request: OpportunitySubscribeRequest,
    user: UserContext = Depends(get_current_user),
) -> OpportunitySubscribeResponse:
    _require_live_agent()
    await check_agent_quota(user, AGENT_ID)

    result = await agent_gateway.forward(
        agent_id=AGENT_ID,
        method="POST",
        path="/subscribe",
        user_id=user["user_id"],
        email=user["email"],
        plan_id=user["plan_id"],
        json_body=request.model_dump(mode="json"),
    )

    asyncio.create_task(
        quota_service.record_usage(
            user_id=user["user_id"],
            agent_id=AGENT_ID,
        )
    )

    return OpportunitySubscribeResponse(**result)


@router.patch("/subscribe", response_model=OpportunitySubscribeResponse)
async def update_subscription(
    request: OpportunitySubscribeRequest,
    user: UserContext = Depends(get_current_user),
) -> OpportunitySubscribeResponse:
    _require_live_agent()

    result = await agent_gateway.forward(
        agent_id=AGENT_ID,
        method="PATCH",
        path="/subscribe",
        user_id=user["user_id"],
        email=user["email"],
        plan_id=user["plan_id"],
        json_body=request.model_dump(mode="json"),
    )

    return OpportunitySubscribeResponse(**result)


@router.post("/unsubscribe")
async def unsubscribe(
    request: OpportunityUnsubscribeRequest,
    user: UserContext = Depends(get_current_user),
) -> Any:
    _require_live_agent()

    return await agent_gateway.forward(
        agent_id=AGENT_ID,
        method="POST",
        path="/unsubscribe",
        user_id=user["user_id"],
        email=user["email"],
        plan_id=user["plan_id"],
        json_body=request.model_dump(mode="json"),
    )
