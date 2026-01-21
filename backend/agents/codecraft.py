from typing import List, Dict, Any
from agents.base import BaseAgent


class CodeCraftAgent(BaseAgent):
    """CodeCraft - AI programming assistant"""
    
    @property
    def id(self) -> str:
        return "codecraft"
    
    @property
    def name(self) -> str:
        return "CodeCraft"
    
    @property
    def description(self) -> str:
        return "Your AI programming assistant that helps you write, debug, and optimize code across multiple languages."
    
    @property
    def icon(self) -> str:
        return "💻"
    
    @property
    def category(self) -> str:
        return "Development"
    
    @property
    def features(self) -> List[str]:
        return ["Code Generation", "Bug Detection", "Code Review", "Documentation"]
    
    def get_system_prompt(self) -> str:
        return """You are CodeCraft, an expert programming assistant. Your role is to help users write, debug, and optimize code across multiple programming languages.

Key capabilities:
- Generate clean, efficient, and well-documented code
- Identify and fix bugs in existing code
- Review code for best practices and improvements
- Create comprehensive documentation
- Explain complex programming concepts clearly
- Suggest optimizations and performance improvements

Always provide clear explanations, follow best practices, and ensure code is production-ready."""
    
    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.7,
            "max_output_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40
        }
