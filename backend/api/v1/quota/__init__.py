"""
Quota API router.

Gives authenticated users visibility into their current usage and limits —
useful for a dashboard or "X requests remaining today" indicator.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends

from core.database import db_manager
from core.dependencies import UserContext, get_current_user

router = APIRouter(prefix="/quota", tags=["quota"])


@router.get("/me", summary="Get current user's quota status")
async def get_my_quota(
    user: UserContext = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Return the authenticated user's quota counters for today and this month,
    along with their plan limits — so the frontend can render usage indicators.
    """
    user_id = user["user_id"]
    plan_id = user["plan_id"]

    # Fetch plan limits
    plan = await db_manager.central["subscription_plans"].find_one({"_id": plan_id}) or {}

    # Fetch all quota docs for this user
    today_key = datetime.utcnow().strftime("%Y-%m-%d")
    month_key = datetime.utcnow().strftime("%Y-%m")

    cursor = db_manager.central["user_quotas"].find({"user_id": user_id})
    quota_docs = await cursor.to_list(length=200)

    # Group by agent_id
    by_agent: Dict[str, Dict] = {}
    for doc in quota_docs:
        aid = doc["agent_id"]
        if aid not in by_agent:
            by_agent[aid] = {"daily_used": 0, "monthly_used": 0}
        if doc["period"] == "daily" and doc["period_key"] == today_key:
            by_agent[aid]["daily_used"] = doc["request_count"]
        if doc["period"] == "monthly" and doc["period_key"] == month_key:
            by_agent[aid]["monthly_used"] = doc["request_count"]

    return {
        "plan_id": plan_id,
        "plan_name": plan.get("name", plan_id),
        "global_daily_limit": plan.get("global_daily_limit", 30),
        "global_monthly_limit": plan.get("global_monthly_limit", 200),
        "by_agent": by_agent,
    }
