"""Chat agent service — execute and conversation history via the gateway."""

from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

from services.agent_catalog import get_agent
from services.agent_gateway import agent_gateway
from services.quota_service import quota_service

logger = logging.getLogger(__name__)


class ChatAgentService:
    async def execute_agent(
        self,
        agent_id: str,
        user_message: str,
        user_id: str,
        user_email: str,
        plan_id: str,
        conversation_id: Optional[str] = None,
    ) -> dict:
        agent = get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")

        result = await agent_gateway.execute(
            agent_id=agent_id,
            user_id=user_id,
            email=user_email,
            plan_id=plan_id,
            message=user_message,
            conversation_id=conversation_id,
        )

        tokens_estimated = (len(user_message) + len(result.get("response", ""))) // 4
        asyncio.create_task(
            quota_service.record_usage(
                user_id=user_id,
                agent_id=agent_id,
                tokens_used=tokens_estimated,
                conversation_id=result.get("conversation_id"),
            )
        )

        return result

    async def get_user_conversations(
        self,
        user_id: str,
        user_email: str,
        plan_id: str,
        agent_id: str,
    ) -> List[dict]:
        return await agent_gateway.get_user_conversations(
            agent_id=agent_id,
            user_id=user_id,
            email=user_email,
            plan_id=plan_id,
        )


chat_service = ChatAgentService()
