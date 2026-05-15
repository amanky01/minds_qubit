"""
FastAPI dependency providers.

The dependency chain enforces authentication and quota in every protected
route with a single  Depends()  call:

    @router.post("/{agent_id}/execute")
    async def execute(
        agent_id: str,
        body: ExecuteRequest,
        ctx: UserContext = Depends(require_quota(agent_id)),   ← one line
    ): ...

Chain:
    require_quota(agent_id)
        └─ get_current_user     (verifies JWT → returns UserContext)
            └─ quota_service.check_quota (raises 429 if exhausted)

UserContext is a typed dict so callers don't have to know the raw key names.
"""

from __future__ import annotations

from typing import Optional, TypedDict

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.database import db_manager
from core.security import decode_token
from services.quota_service import quota_service

_bearer = HTTPBearer()
_optional_bearer = HTTPBearer(auto_error=False)


# ── Typed return shape ─────────────────────────────────────────────────────

class UserContext(TypedDict):
    user_id: str
    email: str
    plan_id: str


# ── Auth dependency ────────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UserContext:
    """
    Validate the Bearer JWT and return a UserContext.
    Raises HTTP 401 on any failure.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[str] = payload.get("sub")
    email: Optional[str] = payload.get("email")

    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch plan_id from the DB (plan may change after token was issued)
    plan_id = await _fetch_plan_id(user_id)

    return UserContext(user_id=user_id, email=email, plan_id=plan_id)


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
) -> Optional[UserContext]:
    """Return a UserContext if a valid token is present, else None."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# ── Quota dependency factory ───────────────────────────────────────────────

def require_quota(agent_id: str):
    """
    Returns a FastAPI dependency that:
      1. Authenticates the user (get_current_user)
      2. Checks their quota for *agent_id*  (QuotaService.check_quota)
      3. Passes the UserContext through to the route handler

    Usage:
        async def my_route(ctx: UserContext = Depends(require_quota("codecraft"))):
            ...

    Or with a path parameter:
        async def my_route(
            agent_id: str,
            ctx: UserContext = Depends(lambda agent_id=agent_id: require_quota(agent_id)()),
        ): ...

    The simpler pattern used in the router is to call it with the path param directly.
    """

    async def _dependency(
        user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        await quota_service.check_quota(
            user_id=user["user_id"],
            agent_id=agent_id,
            plan_id=user["plan_id"],
        )
        return user

    return _dependency


# ── Internal helpers ───────────────────────────────────────────────────────

async def _fetch_plan_id(user_id: str) -> str:
    """
    Retrieve plan_id from the users collection.
    Falls back to 'free' if the document is not found or DB is unavailable.
    """
    try:
        doc = await db_manager.central["users"].find_one(
            {"_id": ObjectId(user_id)},
            {"plan_id": 1},
        )
        return (doc or {}).get("plan_id", "free")
    except Exception:  # noqa: BLE001
        return "free"

