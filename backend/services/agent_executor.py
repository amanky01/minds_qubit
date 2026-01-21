from typing import List, Dict, Any, Optional
from agents.base import BaseAgent
from services.gemini_service import gemini_service
from models.conversation import ConversationInDB, Message
from core.database import get_database
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Service for executing agent interactions"""
    
    async def execute_agent(
        self,
        agent: BaseAgent,
        user_message: str,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent interaction
        
        Args:
            agent: The agent instance to use
            user_message: User's message
            user_id: User ID
            conversation_id: Optional conversation ID to continue existing conversation
        
        Returns:
            Dict with response and conversation_id
        """
        try:
            db = get_database()
            conversations_collection = db["agent_conversations"]
            
            # Get or create conversation
            if conversation_id:
                conversation_doc = await conversations_collection.find_one({"_id": ObjectId(conversation_id)})
                if not conversation_doc or conversation_doc.get("user_id") != user_id:
                    raise ValueError("Conversation not found or access denied")
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in conversation_doc.get("messages", [])
                ]
            else:
                conversation_history = []
            
            # Get agent configuration
            system_prompt = agent.get_system_prompt()
            gemini_config = agent.get_gemini_config()
            
            # Generate response
            response_text = await gemini_service.generate_response(
                system_prompt=system_prompt,
                user_message=user_message,
                conversation_history=conversation_history,
                config=gemini_config
            )
            
            # Add messages to conversation
            new_messages = [
                {"role": "user", "content": user_message, "timestamp": datetime.utcnow()},
                {"role": "assistant", "content": response_text, "timestamp": datetime.utcnow()}
            ]
            
            if conversation_id:
                # Update existing conversation
                await conversations_collection.update_one(
                    {"_id": ObjectId(conversation_id)},
                    {
                        "$push": {"messages": {"$each": new_messages}},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
            else:
                # Create new conversation
                conversation = ConversationInDB(
                    user_id=user_id,
                    agent_id=agent.id,
                    messages=[
                        Message(role=msg["role"], content=msg["content"], timestamp=msg["timestamp"])
                        for msg in new_messages
                    ]
                )
                result = await conversations_collection.insert_one(conversation.dict(by_alias=True))
                conversation_id = str(result.inserted_id)
            
            return {
                "response": response_text,
                "conversation_id": conversation_id,
                "agent_id": agent.id
            }
            
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            raise


# Global instance
agent_executor = AgentExecutor()
