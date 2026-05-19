"""
Template for a new chat agent microservice.

1. Copy this folder to services/agents/<your_id>/
2. Add config to chat_runtime/configs.py (or inline in main.py)
3. Register in backend/services/agent_catalog.py and core env URLs
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_shared"))

from chat_runtime.agent_config import ChatAgentConfig
from chat_runtime.app import create_chat_app

MY_AGENT = ChatAgentConfig(
    id="template",
    name="Template Agent",
    description="Replace with your description.",
    icon="🤖",
    category="General",
    features=["Feature 1"],
    system_prompt="You are a helpful assistant.",
)

app = create_chat_app(MY_AGENT)
