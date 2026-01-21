from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection
from api.v1.router import router as api_router
from agents import initialize_agents
from models.agent import AgentInDB
from core.database import get_database
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def sync_agents_to_mongodb():
    """Sync agent definitions to MongoDB"""
    try:
        from agents import get_all_agents
        
        db = get_database()
        agents_collection = db["agents"]
        agents = get_all_agents()
        
        for agent in agents:
            agent_dict = agent.to_dict()
            
            # Check if agent exists
            existing = await agents_collection.find_one({"id": agent.id})
            
            agent_data = {
                "id": agent_dict["id"],
                "name": agent_dict["name"],
                "description": agent_dict["description"],
                "icon": agent_dict["icon"],
                "category": agent_dict["category"],
                "features": agent_dict["features"],
                "system_prompt": agent_dict["system_prompt"],
                "gemini_config": agent_dict["gemini_config"],
                "is_active": True,
                "updated_at": datetime.utcnow()
            }
            
            if existing:
                # Update existing agent
                await agents_collection.update_one(
                    {"id": agent.id},
                    {"$set": agent_data}
                )
                logger.info(f"Updated agent in MongoDB: {agent.name}")
            else:
                # Insert new agent
                agent_data["created_at"] = datetime.utcnow()
                await agents_collection.insert_one(agent_data)
                logger.info(f"Synced agent to MongoDB: {agent.name}")
        
        logger.info(f"Successfully synced {len(agents)} agents to MongoDB")
    except Exception as e:
        logger.error(f"Error syncing agents to MongoDB: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting up...")
    try:
        await connect_to_mongo()
        initialize_agents()
        await sync_agents_to_mongodb()
    except Exception as e:
        logger.warning(f"Startup warning: {e}")
        # Still initialize agents even if MongoDB fails
        initialize_agents()
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()


app = FastAPI(
    title="AI Agents Platform API",
    description="Backend API for AI Agents Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Agents Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
