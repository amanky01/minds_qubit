"""
MindsQubit Platform — API gateway (core).

Startup: MongoDB, seed plans, sync agent_registry from catalog, ensure indexes.
Agent execution is delegated to microservices via AgentGateway.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.router import router as api_router
from core.config import settings
from core.database import db_manager
from models.quota import DEFAULT_PLANS
from services.agent_catalog import get_all_agents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MindsQubit core starting up…")
    try:
        await db_manager.connect()
        await _seed_plans()
        await _sync_agents()
        await _ensure_indexes()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Startup warning (non-fatal): %s", exc)

    yield

    logger.info("MindsQubit core shutting down…")
    await db_manager.disconnect()


async def _seed_plans() -> None:
    col = db_manager.central["subscription_plans"]
    if await col.count_documents({}) == 0:
        await col.insert_many(DEFAULT_PLANS)
        logger.info("Seeded %d subscription plans", len(DEFAULT_PLANS))


async def _sync_agents() -> None:
    col = db_manager.central["agent_registry"]
    for agent in get_all_agents():
        data = agent.to_dict()
        await col.update_one(
            {"id": agent.id},
            {
                "$set": {**data, "is_active": True, "updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()},
            },
            upsert=True,
        )
    logger.info("Synced %d agents to agent_registry", len(get_all_agents()))


async def _ensure_indexes() -> None:
    central = db_manager.central

    await central["users"].create_index("email", unique=True, background=True)
    await central["user_quotas"].create_index(
        [("user_id", 1), ("agent_id", 1), ("period", 1), ("period_key", 1)],
        unique=True,
        background=True,
    )
    await central["usage_logs"].create_index("user_id", background=True)
    await central["usage_logs"].create_index("created_at", background=True)

    logger.info("MongoDB indexes ensured")


app = FastAPI(
    title="MindsQubit API",
    description="Multi-agent AI platform — API gateway to agent microservices.",
    version="3.0.0",
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
    return {"name": "MindsQubit API", "version": "3.0.0", "docs": "/docs"}


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
