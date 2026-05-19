"""
Registry of per-agent integration routers.

Chat agents use the shared `chat/` router (`/{agent_id}/execute`).
Agents with custom HTTP APIs (subscriptions, webhooks, etc.) add a
subpackage under `api/v1/agents/<agent_id>/` and register the router here.

Mount order matters: fixed-path integration routes must be registered
before parameterized catalog routes like `/{agent_id}`.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter

from api.v1.agents.opportunityalert import router as opportunityalert_router

# Add new integration agent routers to this list.
INTEGRATION_ROUTERS: List[APIRouter] = [
    opportunityalert_router,
]
