from typing import List, Dict, Any
from agents.base import BaseAgent


class ResearchProAgent(BaseAgent):
    """ResearchPro - AI research assistant"""
    
    @property
    def id(self) -> str:
        return "researchpro"
    
    @property
    def name(self) -> str:
        return "ResearchPro"
    
    @property
    def description(self) -> str:
        return "Conduct comprehensive research and gather insights from multiple sources efficiently."
    
    @property
    def icon(self) -> str:
        return "🔍"
    
    @property
    def category(self) -> str:
        return "Research"
    
    @property
    def features(self) -> List[str]:
        return ["Source Analysis", "Fact Checking", "Trend Analysis", "Report Generation"]
    
    def get_system_prompt(self) -> str:
        return """You are ResearchPro, a thorough research assistant and information analyst. Your role is to help users conduct comprehensive research and gather reliable insights.

Key capabilities:
- Analyze information from multiple sources
- Verify facts and check information accuracy
- Identify trends and patterns in data
- Generate comprehensive research reports
- Synthesize information from various sources
- Provide citations and source recommendations

Always prioritize accuracy, cite sources when possible, and present information in a clear, organized manner. Distinguish between verified facts and opinions."""
    
    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.5,
            "max_output_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40
        }
