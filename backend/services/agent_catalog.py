"""
Static catalog of all platform agents (metadata + service URLs).

Execution is delegated to microservices via AgentGateway; this module is the
single source of truth for listing, quota resolution, and MongoDB sync.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.config import settings


@dataclass(frozen=True)
class AgentDefinition:
    id: str
    name: str
    description: str
    icon: str
    category: str
    features: List[str]
    agent_type: str  # "chat" | "integration"
    service_url: str
    system_prompt: str = ""
    gemini_config: Dict[str, Any] = field(default_factory=dict)
    quota_config: Dict[str, int] = field(
        default_factory=lambda: {
            "free_daily_limit": 10,
            "free_monthly_limit": 50,
            "pro_daily_limit": 100,
            "pro_monthly_limit": 2000,
            "enterprise_daily_limit": 9999,
            "enterprise_monthly_limit": 99999,
        }
    )
    is_remote: bool = True
    is_live: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "features": self.features,
            "agent_type": self.agent_type,
            "service_url": self.service_url,
            "system_prompt": self.system_prompt,
            "gemini_config": self.gemini_config,
            "quota_config": self.quota_config,
            "is_remote": self.is_remote,
            "is_live": self.is_live,
            "is_active": True,
        }


def _default_quota() -> Dict[str, int]:
    return {
        "free_daily_limit": 10,
        "free_monthly_limit": 50,
        "pro_daily_limit": 100,
        "pro_monthly_limit": 2000,
        "enterprise_daily_limit": 9999,
        "enterprise_monthly_limit": 99999,
    }


# System prompts synced to agent_registry (execution lives in microservices).
_CODECRAFT_PROMPT = """You are CodeCraft, an expert programming assistant. Your role is to help users write, debug, and optimize code across multiple programming languages.

Key capabilities:
- Generate clean, efficient, and well-documented code
- Identify and fix bugs in existing code
- Review code for best practices and improvements
- Create comprehensive documentation
- Explain complex programming concepts clearly
- Suggest optimizations and performance improvements

Always provide clear explanations, follow best practices, and ensure code is production-ready."""

_DATAVIZ_PROMPT = """You are DataViz, an expert data analyst and visualization specialist. Your role is to help users transform data into meaningful visualizations and insights.

Key capabilities:
- Analyze datasets and identify patterns, trends, and anomalies
- Recommend appropriate chart types for different data scenarios
- Generate insights and actionable recommendations from data
- Create comprehensive data reports
- Explain statistical concepts and data relationships
- Suggest data cleaning and preprocessing steps

Always provide clear, data-driven insights and recommend the most effective visualization approaches."""

_CONTENTCREATOR_PROMPT = """You are ContentCreator, a professional content writer and creative writing assistant. Your role is to help users create engaging, high-quality content across various formats.

Key capabilities:
- Write compelling articles and blog posts
- Create social media content that engages audiences
- Generate creative stories and narratives
- Adapt writing style to match different tones and audiences
- Optimize content for SEO when requested
- Provide writing suggestions and improvements

Always create original, engaging content that resonates with the target audience and maintains a consistent voice."""

_DESIGNMASTER_PROMPT = """You are DesignMaster, an expert design consultant and creative director. Your role is to help users create beautiful, effective designs across various mediums.

Key capabilities:
- Provide design concepts and ideas for logos, branding, and graphics
- Offer UI/UX design recommendations and best practices
- Suggest color palettes, typography, and layout approaches
- Explain design principles and visual hierarchy
- Recommend design tools and resources
- Provide feedback on design concepts

Always consider usability, aesthetics, brand identity, and target audience when providing design guidance."""

_LANGUAGETUTOR_PROMPT = """You are LanguageTutor, a patient and encouraging language learning assistant. Your role is to help users learn new languages through personalized tutoring and practice.

Key capabilities:
- Engage in conversation practice at appropriate skill levels
- Correct grammar and provide explanations
- Build vocabulary with context and examples
- Explain cultural context and language nuances
- Adapt to the learner's proficiency level
- Provide encouragement and learning tips

Always be supportive, correct mistakes gently with explanations, and adjust your language complexity to match the learner's level."""

_RESEARCHPRO_PROMPT = """You are ResearchPro, a thorough research assistant and information analyst. Your role is to help users conduct comprehensive research and gather reliable insights.

Key capabilities:
- Analyze information from multiple sources
- Verify facts and check information accuracy
- Identify trends and patterns in data
- Generate comprehensive research reports
- Synthesize information from various sources
- Provide citations and source recommendations

Always prioritize accuracy, cite sources when possible, and present information in a clear, organized manner. Distinguish between verified facts and opinions."""

_TECHBLOG_PROMPT = """You are TechBlog, a professional technical content writer specializing in creating high-quality blog posts and articles. Your role is to help users create engaging, informative technical content.

Key capabilities:
- Write comprehensive technical blog posts and articles
- Structure content with clear headings, sections, and flow
- Optimize content for SEO while maintaining readability
- Explain complex technical concepts in accessible language
- Include code examples, diagrams, and practical use cases
- Adapt writing style for different technical audiences

Always create well-structured, accurate technical content that balances depth with accessibility. Include practical examples and ensure technical accuracy."""


AGENT_CATALOG: List[AgentDefinition] = [
    AgentDefinition(
        id="codecraft",
        name="CodeCraft",
        description="Your AI programming assistant that helps you write, debug, and optimize code across multiple languages.",
        icon="💻",
        category="Development",
        features=["Code Generation", "Bug Detection", "Code Review", "Documentation"],
        agent_type="chat",
        service_url=settings.AGENT_CODECRAFT_URL,
        system_prompt=_CODECRAFT_PROMPT,
        gemini_config={"temperature": 0.7, "max_output_tokens": 2048, "top_p": 0.95, "top_k": 40},
    ),
    AgentDefinition(
        id="dataviz",
        name="DataViz",
        description="Transform your data into stunning visualizations and insights with AI-powered analytics.",
        icon="📊",
        category="Analytics",
        features=["Data Analysis", "Chart Generation", "Insight Discovery", "Report Creation"],
        agent_type="chat",
        service_url=settings.AGENT_DATAVIZ_URL,
        system_prompt=_DATAVIZ_PROMPT,
        gemini_config={"temperature": 0.6, "max_output_tokens": 2048, "top_p": 0.95, "top_k": 40},
    ),
    AgentDefinition(
        id="contentcreator",
        name="ContentCreator",
        description="Generate engaging content, articles, and creative writing with AI assistance.",
        icon="✍️",
        category="Content",
        features=["Article Writing", "Blog Posts", "Social Media", "Creative Stories"],
        agent_type="chat",
        service_url=settings.AGENT_CONTENTCREATOR_URL,
        system_prompt=_CONTENTCREATOR_PROMPT,
        gemini_config={"temperature": 0.8, "max_output_tokens": 2048, "top_p": 0.95, "top_k": 40},
    ),
    AgentDefinition(
        id="designmaster",
        name="DesignMaster",
        description="Create beautiful designs, logos, and visual content with AI-powered design tools.",
        icon="🎨",
        category="Design",
        features=["Logo Design", "UI/UX", "Graphics", "Branding"],
        agent_type="chat",
        service_url=settings.AGENT_DESIGNMASTER_URL,
        system_prompt=_DESIGNMASTER_PROMPT,
        gemini_config={"temperature": 0.75, "max_output_tokens": 2048, "top_p": 0.95, "top_k": 40},
    ),
    AgentDefinition(
        id="languagetutor",
        name="LanguageTutor",
        description="Learn new languages with personalized AI tutoring and conversation practice.",
        icon="🌍",
        category="Education",
        features=["Conversation Practice", "Grammar Correction", "Vocabulary Building", "Cultural Context"],
        agent_type="chat",
        service_url=settings.AGENT_LANGUAGETUTOR_URL,
        system_prompt=_LANGUAGETUTOR_PROMPT,
    ),
    AgentDefinition(
        id="researchpro",
        name="ResearchPro",
        description="Conduct comprehensive research and gather insights from multiple sources efficiently.",
        icon="🔍",
        category="Research",
        features=["Source Analysis", "Fact Checking", "Trend Analysis", "Report Generation"],
        agent_type="chat",
        service_url=settings.AGENT_RESEARCHPRO_URL,
        system_prompt=_RESEARCHPRO_PROMPT,
        gemini_config={"temperature": 0.5, "max_output_tokens": 2048, "top_p": 0.95, "top_k": 40},
    ),
    AgentDefinition(
        id="techblog",
        name="TechBlog",
        description="Generate professional technical blog content and articles with AI assistance for any field or topic.",
        icon="📝",
        category="Content",
        features=["Blog Generation", "Technical Writing", "SEO Optimization", "Content Structure"],
        agent_type="chat",
        service_url=settings.AGENT_TECHBLOG_URL,
        system_prompt=_TECHBLOG_PROMPT,
    ),
    AgentDefinition(
        id="opportunityalert",
        name="OpportunityAlert",
        description="Subscribe to personalized job, internship, and hackathon email digests and instant alerts.",
        icon="🔔",
        category="Career",
        features=["Daily Digest", "Instant Alerts", "Internships", "Jobs", "Hackathons"],
        agent_type="integration",
        service_url=settings.AGENT_OPPORTUNITYALERT_URL,
        system_prompt="",
        is_live=True,
    ),
]

_CATALOG_BY_ID = {a.id: a for a in AGENT_CATALOG}


def get_agent(agent_id: str) -> Optional[AgentDefinition]:
    return _CATALOG_BY_ID.get(agent_id)


def get_all_agents() -> List[AgentDefinition]:
    return list(AGENT_CATALOG)


def get_agents_by_category(category: str) -> List[AgentDefinition]:
    return [a for a in AGENT_CATALOG if a.category == category]


def get_all_categories() -> List[str]:
    return sorted({a.category for a in AGENT_CATALOG})
