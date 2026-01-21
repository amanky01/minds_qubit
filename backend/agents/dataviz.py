from typing import List, Dict, Any
from agents.base import BaseAgent


class DataVizAgent(BaseAgent):
    """DataViz - AI-powered data visualization and analytics"""
    
    @property
    def id(self) -> str:
        return "dataviz"
    
    @property
    def name(self) -> str:
        return "DataViz"
    
    @property
    def description(self) -> str:
        return "Transform your data into stunning visualizations and insights with AI-powered analytics."
    
    @property
    def icon(self) -> str:
        return "📊"
    
    @property
    def category(self) -> str:
        return "Analytics"
    
    @property
    def features(self) -> List[str]:
        return ["Data Analysis", "Chart Generation", "Insight Discovery", "Report Creation"]
    
    def get_system_prompt(self) -> str:
        return """You are DataViz, an expert data analyst and visualization specialist. Your role is to help users transform data into meaningful visualizations and insights.

Key capabilities:
- Analyze datasets and identify patterns, trends, and anomalies
- Recommend appropriate chart types for different data scenarios
- Generate insights and actionable recommendations from data
- Create comprehensive data reports
- Explain statistical concepts and data relationships
- Suggest data cleaning and preprocessing steps

Always provide clear, data-driven insights and recommend the most effective visualization approaches."""
    
    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.6,
            "max_output_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40
        }
