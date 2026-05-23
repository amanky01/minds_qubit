"""Generic proxy to any agent microservice."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.v1.agents.common import check_agent_quota
from core.dependencies import UserContext, get_current_user
from services.agent_catalog import get_agent
from services.agent_gateway import agent_gateway
from services.quota_service import quota_service

router = APIRouter()

MUTATING_METHODS = frozenset({"POST", "PATCH", "PUT"})


@router.api_route(
    "/{agent_id}/proxy/{path:path}",
    methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
)
async def proxy_to_agent(
    agent_id: str,
    path: str,
    request: Request,
    user: UserContext = Depends(get_current_user),
) -> Any:
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found.",
        )

    if not agent.is_live:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent is not available yet",
        )

    method = request.method.upper()
    if method in MUTATING_METHODS:
        await check_agent_quota(user, agent_id)

    json_body: Optional[dict] = None
    if method in ("POST", "PATCH", "PUT"):
        try:
            body = await request.json()
            if isinstance(body, dict):
                json_body = body
            elif body is not None:
                json_body = {"data": body}
        except Exception:  # noqa: BLE001
            json_body = None

    query_params: Dict[str, str] = dict(request.query_params)

    result = await agent_gateway.forward(
        agent_id=agent_id,
        method=method,
        path=path,
        user_id=user["user_id"],
        email=user["email"],
        plan_id=user["plan_id"],
        json_body=json_body,
        query_params=query_params or None,
    )

    if method == "POST":
        asyncio.create_task(
            quota_service.record_usage(
                user_id=user["user_id"],
                agent_id=agent_id,
            )
        )

    return result
