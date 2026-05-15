"""
Database connection management.

DatabaseManager owns a single AsyncIOMotorClient and exposes two accessors:

    db_manager.central   → mindsqubit_core  (users, plans, quotas, logs)
    db_manager.agent(id) → mindsqubit_agent_<id>  (per-agent conversations etc.)

The per-agent DB handle is cached after the first call so there is no
reconnection overhead on subsequent requests.

Usage (anywhere in the app):
    from core.database import db_manager
    col = db_manager.central["users"]
    col = db_manager.agent("codecraft")["conversations"]
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from core.config import settings

# Motor is imported lazily in connect() so the app can load (e.g. for --help)
# when dependencies are not installed yet, and we can log a clear fix message.

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Owns the Motor client and provides typed DB accessors."""

    def __init__(self) -> None:
        self._client: Any = None
        self._agent_db_cache: Dict[str, Any] = {}

    # ── Lifecycle ──────────────────────────────────────────────────────────

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
            self._agent_db_cache.clear()
            logger.info("Disconnected from MongoDB")

    # ── Accessors ──────────────────────────────────────────────────────────

    @property
    def central(self) -> Any:
        """
        Returns the central platform database (mindsqubit_core).
        Contains: users, subscription_plans, user_quotas, usage_logs, agent_registry.
        """
        self._ensure_connected()
        return self._client[settings.CENTRAL_DB_NAME]  # type: ignore[index]

    def agent(self, agent_id: str) -> Any:
        """
        Returns the database dedicated to *agent_id*.
        Database name: {AGENT_DB_PREFIX}{agent_id}  e.g. mindsqubit_agent_codecraft
        Handles are cached so repeated calls are free.
        """
        self._ensure_connected()
        if agent_id not in self._agent_db_cache:
            db_name = f"{settings.AGENT_DB_PREFIX}{agent_id}"
            self._agent_db_cache[agent_id] = self._client[db_name]  # type: ignore[index]
            logger.debug("Opened agent DB: %s", db_name)
        return self._agent_db_cache[agent_id]

    # ── Internal ───────────────────────────────────────────────────────────

    def _ensure_connected(self) -> None:
        if self._client is None:
            raise ConnectionError(
                "MongoDB is not connected. "
                "Ensure MongoDB is running and MONGODB_URL is correct."
            )


# Module-level singleton — import this everywhere.
db_manager = DatabaseManager()

