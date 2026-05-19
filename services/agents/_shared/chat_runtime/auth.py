from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException, status

from agent_contract.headers import (
    HEADER_PLAN_ID,
    HEADER_SERVICE_KEY,
    HEADER_USER_EMAIL,
    HEADER_USER_ID,
)

from chat_runtime.settings import Settings


@dataclass
class ServiceUserContext:
    user_id: str
    email: str
    plan_id: str


def verify_service_request(
    settings: Settings,
    x_service_key: Optional[str] = Header(None, alias=HEADER_SERVICE_KEY),
    x_user_id: Optional[str] = Header(None, alias=HEADER_USER_ID),
    x_user_email: Optional[str] = Header(None, alias=HEADER_USER_EMAIL),
    x_plan_id: Optional[str] = Header(None, alias=HEADER_PLAN_ID),
) -> ServiceUserContext:
    if settings.AGENT_SERVICE_API_KEY:
        if not x_service_key or x_service_key != settings.AGENT_SERVICE_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service key",
            )
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user context",
        )
    return ServiceUserContext(
        user_id=x_user_id,
        email=x_user_email or "",
        plan_id=x_plan_id or "free",
    )
