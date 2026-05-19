"""Catalog service — list and describe agents from the static registry."""

from __future__ import annotations

from typing import List, Optional

from services.agent_catalog import (
    AgentDefinition,
    get_agent,
    get_all_agents,
    get_agents_by_category,
    get_all_categories,
)


class CatalogService:
    async def get_all_agents(self) -> List[AgentDefinition]:
        return get_all_agents()

    async def get_agent_by_id(self, agent_id: str) -> Optional[AgentDefinition]:
        return get_agent(agent_id)

    async def get_agents_by_category(self, category: str) -> List[AgentDefinition]:
        return get_agents_by_category(category)

    async def get_all_categories(self) -> List[str]:
        return get_all_categories()


catalog_service = CatalogService()
