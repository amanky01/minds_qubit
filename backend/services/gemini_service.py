import google.generativeai as genai
from typing import List, Dict, Any, Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Gemini client
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self.model = None
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. Gemini service will not work.")
        else:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                self.model = None
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a response using Gemini API
        
        Args:
            system_prompt: System prompt/instructions for the agent
            user_message: Current user message
            conversation_history: Previous messages in format [{"role": "user", "content": "..."}, ...]
            config: Gemini configuration (temperature, max_output_tokens, etc.)
        
        Returns:
            Generated response text
        """
        if not self.model:
            raise Exception("Gemini API key not configured")
        
        try:
            # Build conversation history
            history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg.get("role") == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [msg.get("content", "")]
                    })
            
            # Add current user message
            history.append({
                "role": "user",
                "parts": [user_message]
            })
            
            # Create generation config
            generation_config = genai.types.GenerationConfig(
                temperature=config.get("temperature", 0.7) if config else 0.7,
                max_output_tokens=config.get("max_output_tokens", 2048) if config else 2048,
                top_p=config.get("top_p", 0.95) if config else 0.95,
                top_k=config.get("top_k", 40) if config else 40,
            )
            
            # Combine system prompt with conversation
            full_prompt = f"{system_prompt}\n\nConversation:\n"
            
            # Start chat with history
            chat = self.model.start_chat(history=history[:-1] if len(history) > 1 else [])
            
            # Send message with system context
            response = chat.send_message(
                f"{system_prompt}\n\nUser: {user_message}",
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    async def generate_simple_response(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a simple response without conversation history"""
        if not self.model:
            raise Exception("Gemini API key not configured")
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=config.get("temperature", 0.7) if config else 0.7,
                max_output_tokens=config.get("max_output_tokens", 2048) if config else 2048,
                top_p=config.get("top_p", 0.95) if config else 0.95,
                top_k=config.get("top_k", 40) if config else 40,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            raise Exception(f"Failed to generate response: {str(e)}")


# Global instance
gemini_service = GeminiService()
