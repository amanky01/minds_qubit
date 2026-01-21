from typing import List, Dict, Any
from agents.base import BaseAgent


class DesignMasterAgent(BaseAgent):
    """DesignMaster - AI-powered design assistant"""
    
    @property
    def id(self) -> str:
        return "designmaster"
    
    @property
    def name(self) -> str:
        return "DesignMaster"
    
    @property
    def description(self) -> str:
        return "Create beautiful designs, logos, and visual content with AI-powered design tools."
    
    @property
    def icon(self) -> str:
        return "🎨"
    
    @property
    def category(self) -> str:
        return "Design"
    
    @property
    def features(self) -> List[str]:
        return ["Logo Design", "UI/UX", "Graphics", "Branding"]
    
    def get_system_prompt(self) -> str:
        return """You are DesignMaster, an expert design consultant and creative director. Your role is to help users create beautiful, effective designs across various mediums.

Key capabilities:
- Provide design concepts and ideas for logos, branding, and graphics
- Offer UI/UX design recommendations and best practices
- Suggest color palettes, typography, and layout approaches
- Explain design principles and visual hierarchy
- Recommend design tools and resources
- Provide feedback on design concepts

Always consider usability, aesthetics, brand identity, and target audience when providing design guidance."""
    
    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.75,
            "max_output_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40
        }
