"""
Agent API service layer.

Thin orchestration layer between the HTTP router and the domain services
(agent registry, executor, database).  Business logic lives in the domain
services; this layer only translates between HTTP concepts and domain calls.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from agents import get_agent, get_agents_by_category, get_all_agents, get_all_categories
from agents.base import BaseAgent
from core.database import db_manager
from services.agent_executor import agent_executor

logger = logging.getLogger(__name__)


class AgentService:

    # ── Agent registry ─────────────────────────────────────────────────────

    async def get_all_agents(self) -> List[BaseAgent]:
        return get_all_agents()

    async def get_agent_by_id(self, agent_id: str) -> Optional[BaseAgent]:
        return get_agent(agent_id)

    async def get_agents_by_category(self, category: str) -> List[BaseAgent]:
        return get_agents_by_category(category)

    async def get_all_categories(self) -> List[str]:
        return get_all_categories()

    # ── Execution ──────────────────────────────────────────────────────────

    async def execute_agent(
        self,
        agent_id: str,
        user_message: str,
        user_id: str,
        plan_id: str,
        conversation_id: Optional[str] = None,
    ) -> dict:
        """
        Execute one agent turn.
        Raises ValueError if the agent_id is not registered.
        """
        agent = get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")

        return await agent_executor.execute(
            agent=agent,
            user_message=user_message,
            user_id=user_id,
            plan_id=plan_id,
            conversation_id=conversation_id,
        )

    # ── Conversation history ───────────────────────────────────────────────

    async def get_user_conversations(
        self,
        user_id: str,
        agent_id: str,
    ) -> List[dict]:
        """
        Return conversations for a specific (user, agent) pair,
        sorted by most-recently-updated first.
        """
        col = db_manager.agent(agent_id)["conversations"]
        cursor = col.find({"user_id": user_id}).sort("updated_at", -1)
        docs = await cursor.to_list(length=100)

        return [
            {
                "id":         str(doc["_id"]),
                "user_id":    doc["user_id"],
                "agent_id":   doc["agent_id"],
                "title":      doc.get("title"),
                "messages": [
                    {
                        "role":      msg["role"],
                        "content":   msg["content"],
                        "timestamp": msg["timestamp"].isoformat(),
                    }
                    for msg in doc.get("messages", [])
                ],
                "created_at": doc["created_at"].isoformat(),
                "updated_at": doc["updated_at"].isoformat(),
            }
            for doc in docs
        ]


# Module-level singleton
agent_service = AgentService()

