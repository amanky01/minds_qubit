from typing import List, Optional
from agents import get_agent, get_all_agents, get_agents_by_category, get_all_categories
from agents.base import BaseAgent
from services.agent_executor import agent_executor
from core.database import get_database
from bson import ObjectId
from models.agent import AgentInDB
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentService:
    """Service for agent operations"""
    
    async def get_all_agents(self) -> List[BaseAgent]:
        """Get all available agents"""
        return get_all_agents()
    
    async def get_agent_by_id(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return get_agent(agent_id)
    
    async def get_agents_by_category(self, category: str) -> List[BaseAgent]:
        """Get agents by category"""
        return get_agents_by_category(category)
    
    async def get_all_categories(self) -> List[str]:
        """Get all categories"""
        return get_all_categories()
    
    async def execute_agent(
        self,
        agent_id: str,
        user_message: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> dict:
        """Execute an agent interaction"""
        agent = get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        return await agent_executor.execute_agent(
            agent=agent,
            user_message=user_message,
            user_id=user_id,
            conversation_id=conversation_id
        )
    
    async def get_user_conversations(
        self,
        user_id: str,
        agent_id: Optional[str] = None
    ) -> List[dict]:
        """Get user's conversations with agents"""
        db = get_database()
        conversations_collection = db["agent_conversations"]
        
        query = {"user_id": user_id}
        if agent_id:
            query["agent_id"] = agent_id
        
        cursor = conversations_collection.find(query).sort("updated_at", -1)
        conversations = await cursor.to_list(length=100)
        
        result = []
        for conv in conversations:
            result.append({
                "id": str(conv["_id"]),
                "user_id": conv["user_id"],
                "agent_id": conv["agent_id"],
                "messages": [
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg.get("timestamp", conv.get("created_at")).isoformat()
                    }
                    for msg in conv.get("messages", [])
                ],
                "created_at": conv.get("created_at", datetime.utcnow()).isoformat(),
                "updated_at": conv.get("updated_at", datetime.utcnow()).isoformat()
            })
        
        return result


# Global instance
agent_service = AgentService()
