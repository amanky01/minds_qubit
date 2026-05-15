"""
TEMPLATE: How to add a new agent to MindsQubit.

Steps:
    1. Copy this file to  backend/agents/<your_agent_id>.py
    2. Fill in all the abstract properties and methods below
    3. (Optional) Override quota_config if this agent should have different limits
    4. Restart the server — it will be auto-discovered and registered

The platform will automatically:
    ✓ Register the agent in the in-memory registry
    ✓ Sync its metadata to MongoDB agent_registry
    ✓ Create a dedicated database:  mindsqubit_agent_<your_id>
    ✓ Create conversation indexes
    ✓ Apply quota limits based on the user's plan + your quota_config
    ✓ Expose it at  POST /api/v1/agents/<your_id>/execute
"""

from __future__ import annotations

from typing import Any, Dict, List

from agents.base import BaseAgent


class TemplateAgent(BaseAgent):
    """
    Replace this docstring with a description of what your agent does.
    The class name doesn't matter — only the `id` property is used as
    the agent identifier everywhere in the system.
    """

    # ── Required: identity ─────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return "template"          # ← change this (lowercase, no spaces)

    @property
    def name(self) -> str:
        return "Template Agent"    # ← display name

    @property
    def description(self) -> str:
        return "A template agent — replace with your description."

    @property
    def icon(self) -> str:
        return "🤖"               # ← any emoji

    @property
    def category(self) -> str:
        return "General"          # ← used for filtering on the agents page

    @property
    def features(self) -> List[str]:
        return [
            "Feature one",
            "Feature two",
            "Feature three",
        ]

    # ── Required: behaviour ────────────────────────────────────────────────

    def get_system_prompt(self) -> str:
        return """You are Template Agent, an AI assistant on the MindsQubit platform.

Replace this with your agent's specific instructions.  Be detailed — the
quality of your system prompt determines the quality of the agent's responses.

Guidelines:
- Define the persona clearly
- Specify what the agent should and should not do
- Include formatting instructions if relevant
- Add domain-specific knowledge or constraints
"""

    def get_gemini_config(self) -> Dict[str, Any]:
        return {
            "temperature":        0.7,    # 0.0 = deterministic, 1.0 = creative
            "max_output_tokens": 2048,    # max response length
            "top_p":              0.95,
            "top_k":              40,
        }

    # ── Optional: quota overrides ──────────────────────────────────────────
    # Remove this property to use BaseAgent's defaults.

    @property
    def quota_config(self) -> Dict[str, int]:
        return {
            "free_daily_limit":        10,
            "free_monthly_limit":      50,
            "pro_daily_limit":        100,
            "pro_monthly_limit":    2_000,
            "enterprise_daily_limit": 9_999,
            "enterprise_monthly_limit": 99_999,
        }

    # ── Optional: response post-processing ────────────────────────────────
    # Remove this method if no post-processing is needed.

    def process_response(self, raw_response: str) -> str:
        # Example: strip leading/trailing whitespace
        return raw_response.strip()
