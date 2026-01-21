from typing import List, Dict, Any
from agents.base import BaseAgent


class TechBlogAgent(BaseAgent):
    """TechBlog - AI technical blog content generator"""
    
    @property
    def id(self) -> str:
        return "techblog"
    
    @property
    def name(self) -> str:
        return "TechBlog"
    
    @property
    def description(self) -> str:
        return "Generate professional technical blog content and articles with AI assistance for any field or topic."
    
    @property
    def icon(self) -> str:
        return "📝"
    
    @property
    def category(self) -> str:
        return "Content"
    
    @property
    def features(self) -> List[str]:
        return ["Blog Generation", "Technical Writing", "SEO Optimization", "Content Structure"]
    
    def get_system_prompt(self) -> str:
        return """You are TechBlog, a professional technical content writer specializing in creating high-quality blog posts and articles. Your role is to help users create engaging, informative technical content.

Key capabilities:
- Write comprehensive technical blog posts and articles
- Structure content with clear headings, sections, and flow
- Optimize content for SEO while maintaining readability
- Explain complex technical concepts in accessible language
- Include code examples, diagrams, and practical use cases
- Adapt writing style for different technical audiences

Always create well-structured, accurate technical content that balances depth with accessibility. Include practical examples and ensure technical accuracy."""
    
    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.7,
            "max_output_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40
        }
