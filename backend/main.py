"""
MindsQubit Platform — FastAPI application entry point.

Startup sequence
────────────────
1. Connect to MongoDB (central DB + on-demand agent DBs via DatabaseManager)
2. Seed subscription_plans if the collection is empty
3. Auto-discover and register all agent classes from agents/
4. Sync agent metadata to the central agent_registry collection
5. Ensure MongoDB indexes exist for fast quota lookups
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents import get_all_agents, initialize_agents
from api.v1.router import router as api_router
from core.config import settings
from core.database import db_manager
from models.quota import DEFAULT_PLANS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Startup / shutdown ─────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MindsQubit starting up…")
    try:
        await db_manager.connect()
        await _seed_plans()
        initialize_agents()
        await _sync_agents()
        await _ensure_indexes()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Startup warning (non-fatal): %s", exc)
        initialize_agents()   # still register agents even if DB is down

    yield   # ← application runs here

    logger.info("MindsQubit shutting down…")
    await db_manager.disconnect()


async def _seed_plans() -> None:
    """Insert default subscription plans if the collection is empty."""
    col = db_manager.central["subscription_plans"]
    if await col.count_documents({}) == 0:
        await col.insert_many(DEFAULT_PLANS)
        logger.info("Seeded %d subscription plans", len(DEFAULT_PLANS))


async def _sync_agents() -> None:
    """Mirror in-memory agent registry to MongoDB (upsert on agent id)."""
    col = db_manager.central["agent_registry"]
    agents = get_all_agents()
    for agent in agents:
        data = agent.to_dict()
        await col.update_one(
            {"id": agent.id},
            {
                "$set": {**data, "is_active": True, "updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()},
            },
            upsert=True,
        )
    logger.info("Synced %d agents to agent_registry", len(agents))


async def _ensure_indexes() -> None:
    """
    Create indexes that are critical for performance.
    MongoDB skips creation if the index already exists.
    """
    central = db_manager.central

    # users — fast email lookup during login
    await central["users"].create_index("email", unique=True, background=True)

    # user_quotas — compound unique index for O(1) quota reads
    await central["user_quotas"].create_index(
        [("user_id", 1), ("agent_id", 1), ("period", 1), ("period_key", 1)],
        unique=True,
        background=True,
    )

    # usage_logs — time-series and per-user queries
    await central["usage_logs"].create_index("user_id", background=True)
    await central["usage_logs"].create_index("created_at", background=True)

    # Per-agent conversation indexes
    for agent in get_all_agents():
        if agent.has_own_db:
            agent_db = db_manager.agent(agent.id)
            await agent_db["conversations"].create_index(
                [("user_id", 1), ("updated_at", -1)], background=True
            )

    logger.info("MongoDB indexes ensured")


# ── App factory ────────────────────────────────────────────────────────────

app = FastAPI(
    title="MindsQubit API",
    description="Multi-agent AI platform — modular, quota-aware, startup-ready.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["meta"])
async def root():
    return {"name": "MindsQubit API", "version": "2.0.0", "docs": "/docs"}


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info",
    )
