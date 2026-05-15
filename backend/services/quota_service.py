"""
Quota Service.

Responsibilities
────────────────
1. check_quota(user_id, agent_id, plan_id)
   Raises QuotaExceededError (→ HTTP 429) if the user has exhausted their
   daily or monthly allowance for the requested agent.

2. record_usage(user_id, agent_id, tokens_used, latency_ms, ...)
   Atomically increments rolling counters (daily + monthly) and appends
   an immutable UsageLog entry.  Designed to be called with
   asyncio.create_task() so it never blocks the HTTP response.

Limit resolution priority (highest wins)
─────────────────────────────────────────
  1. agent_overrides in the user's SubscriptionPlan for this specific agent
  2. Agent's own quota_config for the user's plan tier
  3. global_daily_limit / global_monthly_limit from SubscriptionPlan

Design notes
────────────
- All counter increments use upsert + $inc for atomicity — no race
  conditions even under concurrent requests.
- Plan documents are fetched once per request (tiny document, indexed _id).
  A Redis cache layer can be added later with zero changes to callers.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from agents import get_agent
from core.database import db_manager

logger = logging.getLogger(__name__)

# ── Custom exception ──────────────────────────────────────────────────────────

class QuotaExceededError(HTTPException):
    """Raised when a user's request quota is exhausted."""

    def __init__(self, period: str, limit: int, used: int) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "quota_exceeded",
                "period": period,
                "limit": limit,
                "used": used,
                "message": (
                    f"You have reached your {period} limit of {limit} requests. "
                    "Upgrade your plan or wait for the period to reset."
                ),
            },
        )


# ── Quota Service ─────────────────────────────────────────────────────────────

class QuotaService:
    """
    Stateless service — all state lives in MongoDB.
    Instantiated once as a module-level singleton.
    """

    # ── Public API ────────────────────────────────────────────────────────

    async def check_quota(
        self,
        user_id: str,
        agent_id: str,
        plan_id: str,
    ) -> None:
        """
        Verify the user is within quota for agent_id.
        Raises QuotaExceededError (HTTP 429) if any limit is breached.
        """
        plan = await self._get_plan(plan_id)
        if plan is None:
            # Unknown plan → fall back to free limits to be safe
            logger.warning("Unknown plan_id=%s for user=%s; using free defaults", plan_id, user_id)
            plan = await self._get_plan("free") or {}

        daily_limit, monthly_limit = self._resolve_limits(plan, agent_id)

        daily_count = await self._get_count(user_id, agent_id, "daily")
        if daily_count >= daily_limit:
            raise QuotaExceededError("daily", daily_limit, daily_count)

        monthly_count = await self._get_count(user_id, agent_id, "monthly")
        if monthly_count >= monthly_limit:
            raise QuotaExceededError("monthly", monthly_limit, monthly_count)

    async def record_usage(
        self,
        user_id: str,
        agent_id: str,
        tokens_used: int = 0,
        latency_ms: int = 0,
        conversation_id: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """
        Increment rolling counters and write an audit log entry.
        Safe to fire-and-forget via asyncio.create_task().
        All DB errors are caught and logged — they must never crash a request.
        """
        try:
            await asyncio.gather(
                self._increment_counter(user_id, agent_id, "daily"),
                self._increment_counter(user_id, agent_id, "monthly"),
                self._write_log(
                    user_id=user_id,
                    agent_id=agent_id,
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    conversation_id=conversation_id,
                    status=status,
                    error_message=error_message,
                ),
            )
        except Exception as exc:  # noqa: BLE001
            # Never let logging failures bubble up to the caller
            logger.error("Failed to record usage for user=%s agent=%s: %s", user_id, agent_id, exc)

    # ── Private helpers ───────────────────────────────────────────────────

    async def _get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a plan document from central DB by _id."""
        try:
            return await db_manager.central["subscription_plans"].find_one(
                {"_id": plan_id}
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Could not fetch plan %s: %s", plan_id, exc)
            return None

    def _resolve_limits(
        self, plan: Dict[str, Any], agent_id: str
    ) -> tuple[int, int]:
        """
        Return (daily_limit, monthly_limit) for this agent under this plan.
        Priority: agent_overrides > agent.quota_config > plan global limits.
        """
        # 1. Check plan-level per-agent override
        agent_overrides: Dict[str, Any] = plan.get("agent_overrides", {})
        if agent_id in agent_overrides:
            override = agent_overrides[agent_id]
            return override["daily_limit"], override["monthly_limit"]

        # 2. Check the agent's own declared quota defaults for this plan tier
        agent = get_agent(agent_id)
        if agent is not None:
            plan_id: str = plan.get("_id", "free")
            qc = agent.quota_config
            daily_key = f"{plan_id}_daily_limit"
            monthly_key = f"{plan_id}_monthly_limit"
            if daily_key in qc and monthly_key in qc:
                return qc[daily_key], qc[monthly_key]

        # 3. Fall back to plan-wide global limits
        return (
            plan.get("global_daily_limit", 10),
            plan.get("global_monthly_limit", 50),
        )

    async def _get_count(
        self, user_id: str, agent_id: str, period: str
    ) -> int:
        """Return the current counter value (0 if the doc doesn't exist yet)."""
        period_key = self._period_key(period)
        doc = await db_manager.central["user_quotas"].find_one(
            {
                "user_id": user_id,
                "agent_id": agent_id,
                "period": period,
                "period_key": period_key,
            },
            {"request_count": 1},
        )
        return doc["request_count"] if doc else 0

    async def _increment_counter(
        self, user_id: str, agent_id: str, period: str
    ) -> None:
        """
        Atomically upsert the quota counter.
        Using $inc + upsert guarantees correctness under concurrent requests.
        """
        period_key = self._period_key(period)
        await db_manager.central["user_quotas"].update_one(
            {
                "user_id": user_id,
                "agent_id": agent_id,
                "period": period,
                "period_key": period_key,
            },
            {
                "$inc": {"request_count": 1},
                "$set": {"last_request_at": datetime.utcnow()},
                "$setOnInsert": {"token_count": 0},
            },
            upsert=True,
        )

    async def _write_log(
        self,
        user_id: str,
        agent_id: str,
        tokens_used: int,
        latency_ms: int,
        conversation_id: Optional[str],
        status: str,
        error_message: Optional[str],
    ) -> None:
        """Append one immutable usage log entry."""
        await db_manager.central["usage_logs"].insert_one(
            {
                "user_id": user_id,
                "agent_id": agent_id,
                "conversation_id": conversation_id,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "status": status,
                "error_message": error_message,
                "created_at": datetime.utcnow(),
            }
        )

    @staticmethod
    def _period_key(period: str) -> str:
        """Return the string key for the current period window."""
        now = datetime.utcnow()
        if period == "daily":
            return now.strftime("%Y-%m-%d")
        return now.strftime("%Y-%m")


# Module-level singleton
quota_service = QuotaService()
