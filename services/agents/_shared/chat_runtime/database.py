from __future__ import annotations

import logging
from typing import Any, Optional

from chat_runtime.settings import Settings

logger = logging.getLogger(__name__)


class AgentDatabase:
    def __init__(self) -> None:
        self._client: Any = None
        self._db: Any = None

    async def connect(self, settings: Settings) -> None:
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ModuleNotFoundError:
            logger.error("motor is required for agent services")
            return

        try:
            self._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5_000,
            )
            await self._client.admin.command("ping")
            self._db = self._client[settings.db_name]
            await self._db["conversations"].create_index(
                [("user_id", 1), ("updated_at", -1)],
                background=True,
            )
            logger.info("Connected to agent DB %s", settings.db_name)
        except Exception as exc:  # noqa: BLE001
            logger.warning("MongoDB connection failed: %s", exc)

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None

    @property
    def conversations(self) -> Any:
        if self._db is None:
            raise ConnectionError("Agent database is not connected")
        return self._db["conversations"]


agent_db = AgentDatabase()
