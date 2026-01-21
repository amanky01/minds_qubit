from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the agent"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of the agent"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the agent does"""
        pass
    
    @property
    @abstractmethod
    def icon(self) -> str:
        """Icon/emoji for the agent"""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Category the agent belongs to"""
        pass
    
    @property
    @abstractmethod
    def features(self) -> List[str]:
        """List of features the agent provides"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt for Gemini"""
        pass
    
    @abstractmethod
    def get_gemini_config(self) -> Dict[str, Any]:
        """Return agent-specific Gemini configuration"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "features": self.features,
            "system_prompt": self.get_system_prompt(),
            "gemini_config": self.get_gemini_config()
        }
