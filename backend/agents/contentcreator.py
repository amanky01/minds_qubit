from typing import List, Dict, Any
from agents.base import BaseAgent


class ContentCreatorAgent(BaseAgent):
    """ContentCreator - AI content generation assistant"""
    
    @property
    def id(self) -> str:
        return "contentcreator"
    
    @property
    def name(self) -> str:
        return "ContentCreator"
    
    @property
    def description(self) -> str:
        return "Generate engaging content, articles, and creative writing with AI assistance."
    
    @property
    def icon(self) -> str:
        return "✍️"
    
    @property
    def category(self) -> str:
        return "Content"
    
    @property
    def features(self) -> List[str]:
        return ["Article Writing", "Blog Posts", "Social Media", "Creative Stories"]
    
    def get_system_prompt(self) -> str:
        return """You are ContentCreator, a professional content writer and creative writing assistant. Your role is to help users create engaging, high-quality content across various formats.

Key capabilities:
- Write compelling articles and blog posts
- Create social media content that engages audiences
- Generate creative stories and narratives
- Adapt writing style to match different tones and audiences
- Optimize content for SEO when requested
- Provide writing suggestions and improvements

Always create original, engaging content that resonates with the target audience and maintains a consistent voice."""
    
    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.8,
            "max_output_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40
        }
