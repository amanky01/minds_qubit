"""
Agent Executor.

Orchestrates a single agent interaction:
    1. Load or create conversation (from per-agent DB)
    2. Call Gemini via GeminiService
    3. Persist messages back to per-agent DB
    4. Fire-and-forget usage recording (does not block response)

This class deliberately knows nothing about quota limits — that
responsibility lives in QuotaService and is enforced by the dependency
layer before the executor is ever called.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from bson import ObjectId

from agents.base import BaseAgent
from core.database import db_manager
from models.conversation import ConversationInDB, Message
from services.gemini_service import gemini_service
from services.quota_service import quota_service

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Stateless executor — all state is stored in MongoDB."""

    async def execute(
        self,
        agent: BaseAgent,
        user_message: str,
        user_id: str,
        plan_id: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run one round-trip with the agent.

        Args:
            agent:           The instantiated agent to use.
            user_message:    The user's text input.
            user_id:         Authenticated user's ID (string).
            plan_id:         The user's subscription plan (for usage logging).
            conversation_id: Existing conversation to continue, or None.

        Returns:
            {
                "response":        str,
                "conversation_id": str,
                "agent_id":        str,
            }
        """
        start_ms = int(time.monotonic() * 1000)

        conv_col = db_manager.agent(agent.id)["conversations"]

        # ── Load or create conversation ────────────────────────────────────
        conversation_history: List[Dict[str, str]] = []

        if conversation_id:
            doc = await conv_col.find_one({"_id": ObjectId(conversation_id)})
            if not doc or doc.get("user_id") != user_id:
                raise ValueError("Conversation not found or access denied")
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in doc.get("messages", [])
            ]

        # ── Call Gemini ────────────────────────────────────────────────────
        raw_response = await gemini_service.generate_response(
            system_prompt=agent.get_system_prompt(),
            user_message=user_message,
            conversation_history=conversation_history,
            config=agent.get_gemini_config(),
        )

        # Allow the agent to post-process the response (optional hook)
        response_text = agent.process_response(raw_response)

        latency_ms = int(time.monotonic() * 1000) - start_ms

        # ── Persist messages ───────────────────────────────────────────────
        now_ts = __import__("datetime").datetime.utcnow()
        new_messages = [
            {"role": "user",      "content": user_message,  "timestamp": now_ts},
            {"role": "assistant", "content": response_text, "timestamp": now_ts},
        ]

        if conversation_id:
            await conv_col.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$push": {"messages": {"$each": new_messages}},
                    "$set":  {"updated_at": now_ts},
                },
            )
        else:
            # Auto-generate a title from the first user message (first 60 chars)
            title = user_message[:60].rstrip() + ("…" if len(user_message) > 60 else "")
            conv = ConversationInDB(
                user_id=user_id,
                agent_id=agent.id,
                title=title,
                messages=[
                    Message(role=m["role"], content=m["content"], timestamp=now_ts)
                    for m in new_messages
                ],
            )
            result = await conv_col.insert_one(
                conv.model_dump(by_alias=True, exclude_none=True)
            )
            conversation_id = str(result.inserted_id)

        # ── Record usage (non-blocking) ────────────────────────────────────
        # Estimate token count: ~4 chars per token is a good rough heuristic
        tokens_estimated = (len(user_message) + len(response_text)) // 4
        asyncio.create_task(
            quota_service.record_usage(
                user_id=user_id,
                agent_id=agent.id,
                tokens_used=tokens_estimated,
                latency_ms=latency_ms,
                conversation_id=conversation_id,
            )
        )

        return {
            "response":        response_text,
            "conversation_id": conversation_id,
            "agent_id":        agent.id,
        }


# Module-level singleton
agent_executor = AgentExecutor()

