from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB: {e}")
        logger.warning("Server will start but database operations will fail. Please start MongoDB.")
        # Don't raise - allow server to start without MongoDB for development
        # In production, you might want to raise here

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    if db.client is None:
        raise ConnectionError("MongoDB is not connected. Please ensure MongoDB is running and MONGODB_URL is correct.")
    return db.client[settings.DATABASE_NAME]
