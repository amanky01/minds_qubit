"""OpportunityAlert-specific routes (subscription proxy to crawler service)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.v1.agents.common import check_agent_quota
from api.v1.agents.opportunityalert.schemas import (
    OpportunitySubscribeRequest,
    OpportunitySubscribeResponse,
    OpportunityUnsubscribeRequest,
)
from api.v1.agents.opportunityalert.service import (
    AGENT_ID,
    opportunityalert_service,
)
from core.dependencies import UserContext, get_current_user
from services.quota_service import quota_service

router = APIRouter(prefix="/opportunityalert", tags=["opportunityalert"])


@router.post("/subscribe", response_model=OpportunitySubscribeResponse)
async def subscribe(
    request: OpportunitySubscribeRequest,
    user: UserContext = Depends(get_current_user),
) -> OpportunitySubscribeResponse:
    await check_agent_quota(user, AGENT_ID)
    result = await opportunityalert_service.subscribe(
        user_id=user["user_id"],
        user_email=user["email"],
        plan_id=user["plan_id"],
        body=request.model_dump(mode="json"),
    )
    await quota_service.record_usage(
        user_id=user["user_id"],
        agent_id=AGENT_ID,
    )
    return OpportunitySubscribeResponse(**result)


@router.patch("/subscribe", response_model=OpportunitySubscribeResponse)
async def update_subscription(
    request: OpportunitySubscribeRequest,
    user: UserContext = Depends(get_current_user),
) -> OpportunitySubscribeResponse:
    result = await opportunityalert_service.update_subscription(
        user_id=user["user_id"],
        user_email=user["email"],
        plan_id=user["plan_id"],
        body=request.model_dump(mode="json"),
    )
    return OpportunitySubscribeResponse(**result)


@router.post("/unsubscribe")
async def unsubscribe(
    request: OpportunityUnsubscribeRequest,
    user: UserContext = Depends(get_current_user),
) -> dict:
    return await opportunityalert_service.unsubscribe(
        user_id=user["user_id"],
        user_email=user["email"],
        plan_id=user["plan_id"],
        body=request.model_dump(mode="json"),
    )
