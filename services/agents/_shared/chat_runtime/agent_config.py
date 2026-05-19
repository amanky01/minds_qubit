from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ChatAgentConfig:
    id: str
    name: str
    description: str
    icon: str
    category: str
    features: List[str]
    system_prompt: str
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
