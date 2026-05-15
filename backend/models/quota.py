"""
Quota & billing models.

Three collections live in the central database:

  subscription_plans  — what each plan allows
  user_quotas         — rolling counters (daily / monthly) per (user, agent)
  usage_logs          — append-only audit trail for every request
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from models.shared import PyObjectId


# ── Subscription Plans ──────────────────────────────────────────────────────

class AgentQuotaOverride(BaseModel):
    """Per-agent limit override that supersedes the plan-level defaults."""
    daily_limit: int
    monthly_limit: int


class SubscriptionPlan(BaseModel):
    """
    Stored in central DB → subscription_plans collection.
    _id is a human-readable string: 'free' | 'pro' | 'enterprise'
    """
    id: str = Field(alias="_id")           # 'free', 'pro', 'enterprise'
    name: str                               # display name
    price_monthly_usd: float = 0.0
    global_daily_limit: int                 # requests/day across all agents
    global_monthly_limit: int
    # Optional per-agent overrides  { "codecraft": { daily_limit: 50, ... } }
    agent_overrides: Dict[str, AgentQuotaOverride] = Field(default_factory=dict)
    is_active: bool = True

    model_config = {"populate_by_name": True}


# ── User Quotas (rolling counters) ──────────────────────────────────────────

class UserQuota(BaseModel):
    """
    One document per (user_id, agent_id, period, period_key).

    compound unique index:
        user_id + agent_id + period + period_key

    This makes quota lookups a single O(1) index read.
    Counters are incremented atomically via  $inc  + upsert.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str                # str representation of user ObjectId
    agent_id: str               # e.g. 'codecraft'
    period: str                 # 'daily' | 'monthly'
    period_key: str             # 'YYYY-MM-DD' (daily) | 'YYYY-MM' (monthly)
    request_count: int = 0
    token_count: int = 0
    last_request_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


# ── Usage Logs (append-only audit trail) ────────────────────────────────────

class UsageLog(BaseModel):
    """
    One document per agent execution.
    Never updated after insert — treated as an immutable event log.
    Useful for: billing, analytics, debugging, SLA monitoring.
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    agent_id: str
    conversation_id: Optional[str] = None
    tokens_used: int = 0
    latency_ms: int = 0
    status: str = "success"     # 'success' | 'error' | 'quota_exceeded'
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


# ── Default plan seed data ──────────────────────────────────────────────────

DEFAULT_PLANS: list[Dict[str, Any]] = [
    {
        "_id": "free",
        "name": "Free Tier",
        "price_monthly_usd": 0.0,
        "global_daily_limit": 30,
        "global_monthly_limit": 200,
        "agent_overrides": {},
        "is_active": True,
    },
    {
        "_id": "pro",
        "name": "Pro",
        "price_monthly_usd": 9.0,
        "global_daily_limit": 300,
        "global_monthly_limit": 5000,
        "agent_overrides": {},
        "is_active": True,
    },
    {
        "_id": "enterprise",
        "name": "Enterprise",
        "price_monthly_usd": 49.0,
        "global_daily_limit": 9999,
        "global_monthly_limit": 99999,
        "agent_overrides": {},
        "is_active": True,
    },
]
