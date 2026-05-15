"""
BaseAgent — abstract base class for every MindsQubit agent.

To add a new agent:
    1. Create  backend/agents/<yourname>.py
    2. Subclass BaseAgent and implement the abstract properties/methods
    3. (Optional) override quota_config to set custom limits
    4. Restart — the agent is auto-discovered and registered

Design principles
─────────────────
- Required fields are abstract properties → Python enforces them at
  class definition time (not at first use), catching missing fields early.
- quota_config provides sensible defaults; each agent can override.
- process_response() is an optional hook for post-processing Gemini output
  (e.g. stripping markdown fences, formatting JSON) without touching the
  executor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    """Abstract base class for all AI agents on the MindsQubit platform."""

    # ── Identity (required) ────────────────────────────────────────────────

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique slug used as the agent_id everywhere (URL, DB key, etc.)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description shown on the agents listing page."""

    @property
    @abstractmethod
    def icon(self) -> str:
        """Emoji or icon string for UI display."""

    @property
    @abstractmethod
    def category(self) -> str:
        """Category string used for filtering (e.g. 'Development')."""

    @property
    @abstractmethod
    def features(self) -> List[str]:
        """Feature bullet points shown on the agent card."""

    # ── Behaviour (required) ───────────────────────────────────────────────

    @abstractmethod
    def get_system_prompt(self) -> str:
        """System prompt injected into every Gemini conversation."""

    @abstractmethod
    def get_gemini_config(self) -> Dict[str, Any]:
        """
        Gemini generation config.
        Expected keys: temperature, max_output_tokens, top_p, top_k
        """

    # ── Quota configuration (optional override) ────────────────────────────

    @property
    def quota_config(self) -> Dict[str, int]:
        """
        Per-plan daily and monthly request limits for this agent.

        Keys follow the pattern: {plan_id}_daily_limit / {plan_id}_monthly_limit
        The QuotaService looks up the user's plan_id and reads the matching keys.
        Add a key pair for every plan you define in subscription_plans.

        Override in subclasses to set agent-specific limits.
        """
        return {
            "free_daily_limit": 10,
            "free_monthly_limit": 50,
            "pro_daily_limit": 100,
            "pro_monthly_limit": 2_000,
            "enterprise_daily_limit": 9_999,
            "enterprise_monthly_limit": 99_999,
        }

    # ── Database (optional override) ───────────────────────────────────────

    @property
    def has_own_db(self) -> bool:
        """
        Return True (default) to give this agent its own MongoDB database.
        Set to False for stateless agents that don't persist conversations.
        """
        return True

    @property
    def db_name(self) -> str:
        """Computed database name — override only if you need a custom name."""
        from core.config import settings
        return f"{settings.AGENT_DB_PREFIX}{self.id}"

    # ── Response post-processing (optional override) ───────────────────────

    def process_response(self, raw_response: str) -> str:
        """
        Optional hook called after Gemini returns a response.
        Default implementation returns the response unchanged.
        Subclasses can strip markdown, reformat JSON, etc.
        """
        return raw_response

    # ── Serialisation ──────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent metadata to a plain dict for MongoDB / API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "features": self.features,
            "system_prompt": self.get_system_prompt(),
            "gemini_config": self.get_gemini_config(),
            "quota_config": self.quota_config,
            "has_own_db": self.has_own_db,
            "db_name": self.db_name,
        }

