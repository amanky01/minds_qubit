from typing import List, Dict, Any
from agents.base import BaseAgent


class LanguageTutorAgent(BaseAgent):
    """LanguageTutor - AI language learning assistant"""
    
    @property
    def id(self) -> str:
        return "languagetutor"
    
    @property
    def name(self) -> str:
        return "LanguageTutor"
    
    @property
    def description(self) -> str:
        return "Learn new languages with personalized AI tutoring and conversation practice."
    
    @property
    def icon(self) -> str:
        return "🌍"
    
    @property
    def category(self) -> str:
        return "Education"
    
    @property
    def features(self) -> List[str]:
        return ["Conversation Practice", "Grammar Correction", "Vocabulary Building", "Cultural Context"]
    
    def get_system_prompt(self) -> str:
        return """You are LanguageTutor, a patient and encouraging language learning assistant. Your role is to help users learn new languages through personalized tutoring and practice.

Key capabilities:
- Engage in conversation practice at appropriate skill levels
- Correct grammar and provide explanations
- Build vocabulary with context and examples
- Explain cultural context and language nuances
- Adapt to the learner's proficiency level
- Provide encouragement and learning tips

Always be supportive, correct mistakes gently with explanations, and adjust your language complexity to match the learner's level."""
    
    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.7,
            "max_output_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40
        }
