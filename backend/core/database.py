"""
Database connection management for the core API gateway.

The core only accesses the central platform database (mindsqubit_core).
Per-agent conversation data lives in each chat microservice's MongoDB database.
"""

from __future__ import annotations

import logging
from typing import Any

from core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Owns the Motor client and provides access to the central database."""

    def __init__(self) -> None:
        self._client: Any = None

    async def connect(self) -> None:
        """Open the connection and verify reachability."""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ModuleNotFoundError:
            logger.error(
                "Missing Python package 'motor'. On macOS/Homebrew Python, use a venv:\n"
                "  cd backend && python3 -m venv .venv && source .venv/bin/activate\n"
                "  pip install -r requirements.txt\n"
                "  uvicorn main:app --reload\n"
                "Or run: backend/.venv/bin/uvicorn main:app --reload"
            )
            return

        try:
            self._client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5_000,
            )
            await self._client.admin.command("ping")
            logger.info("Connected to MongoDB at %s", settings.MONGODB_URL)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Could not connect to MongoDB: %s — "
                "server will start but DB operations will fail.",
                exc,
            )

    async def disconnect(self) -> None:
        """Close the connection gracefully."""
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("Disconnected from MongoDB")

    @property
    def central(self) -> Any:
        """
        Central platform database (mindsqubit_core).
        Collections: users, subscription_plans, user_quotas, usage_logs, agent_registry.
        """
        self._ensure_connected()
        return self._client[settings.CENTRAL_DB_NAME]  # type: ignore[index]

    def _ensure_connected(self) -> None:
        if self._client is None:
            raise ConnectionError(
                "MongoDB is not connected. "
                "Ensure MongoDB is running and MONGODB_URL is correct."
            )


db_manager = DatabaseManager()
