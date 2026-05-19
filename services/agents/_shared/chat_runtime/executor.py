from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId

from agent_contract.schemas import ExecuteResponse
from chat_runtime.auth import ServiceUserContext
from chat_runtime.database import agent_db
from chat_runtime.gemini_service import GeminiService


class ChatExecutor:
    def __init__(
        self,
        agent_id: str,
        system_prompt: str,
        gemini_config: Dict[str, Any],
        gemini: GeminiService,
    ) -> None:
        self.agent_id = agent_id
        self.system_prompt = system_prompt
        self.gemini_config = gemini_config
        self.gemini = gemini

    async def execute(
        self,
        user: ServiceUserContext,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> ExecuteResponse:
        col = agent_db.conversations
        conversation_history: List[Dict[str, str]] = []

        if conversation_id:
            doc = await col.find_one({"_id": ObjectId(conversation_id)})
            if not doc or doc.get("user_id") != user.user_id:
                raise ValueError("Conversation not found or access denied")
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in doc.get("messages", [])
            ]

        response_text = await self.gemini.generate_response(
            system_prompt=self.system_prompt,
            user_message=message,
            conversation_history=conversation_history,
            config=self.gemini_config,
        )

        now_ts = datetime.utcnow()
        new_messages = [
            {"role": "user", "content": message, "timestamp": now_ts},
            {"role": "assistant", "content": response_text, "timestamp": now_ts},
        ]

        if conversation_id:
            await col.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$push": {"messages": {"$each": new_messages}},
                    "$set": {"updated_at": now_ts},
                },
            )
        else:
            title = message[:60].rstrip() + ("…" if len(message) > 60 else "")
            result = await col.insert_one(
                {
                    "user_id": user.user_id,
                    "agent_id": self.agent_id,
                    "title": title,
                    "messages": new_messages,
                    "metadata": {},
                    "created_at": now_ts,
                    "updated_at": now_ts,
                }
            )
            conversation_id = str(result.inserted_id)

        return ExecuteResponse(
            response=response_text,
            conversation_id=conversation_id,
            agent_id=self.agent_id,
        )

    async def list_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        col = agent_db.conversations
        cursor = col.find({"user_id": user_id}).sort("updated_at", -1)
        docs = await cursor.to_list(length=100)
        return [
            {
                "id": str(doc["_id"]),
                "user_id": doc["user_id"],
                "agent_id": doc["agent_id"],
                "title": doc.get("title"),
                "messages": [
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg["timestamp"].isoformat(),
                    }
                    for msg in doc.get("messages", [])
                ],
                "created_at": doc["created_at"].isoformat(),
                "updated_at": doc["updated_at"].isoformat(),
            }
            for doc in docs
        ]
