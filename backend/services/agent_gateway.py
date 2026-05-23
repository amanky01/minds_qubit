"""
HTTP gateway from MindsQubit core to agent microservices.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from core.config import settings
from services.agent_catalog import AgentDefinition, get_agent

logger = logging.getLogger(__name__)

HEADER_USER_ID = "X-User-Id"
HEADER_USER_EMAIL = "X-User-Email"
HEADER_PLAN_ID = "X-Plan-Id"

REQUEST_TIMEOUT = 60.0


class AgentGateway:
    def _headers(self, user_id: str, email: str, plan_id: str) -> Dict[str, str]:
        headers = {
            HEADER_USER_ID: user_id,
            HEADER_USER_EMAIL: email or "",
            HEADER_PLAN_ID: plan_id or "free",
        }
        return headers

    def _agent(self, agent_id: str) -> AgentDefinition:
        agent = get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")
        if not agent.service_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Agent '{agent_id}' service URL is not configured",
            )
        return agent

    @staticmethod
    def _normalize_path(path: str) -> str:
        clean = path.lstrip("/")
        if ".." in clean.split("/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid proxy path",
            )
        return clean

    async def forward(
        self,
        agent_id: str,
        method: str,
        path: str,
        user_id: str,
        email: str,
        plan_id: str,
        json_body: Optional[dict] = None,
        query_params: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Forward an HTTP request to the agent microservice."""
        agent = self._agent(agent_id)
        rel_path = self._normalize_path(path)
        url = f"{agent.service_url.rstrip('/')}/{rel_path}"

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.request(
                    method.upper(),
                    url,
                    json=json_body if method.upper() != "GET" else None,
                    params=query_params,
                    headers=self._headers(user_id, email, plan_id),
                )
        except httpx.RequestError as exc:
            logger.error("Agent service unreachable agent=%s: %s", agent_id, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Agent service '{agent_id}' is unavailable",
            ) from exc

        if response.status_code >= 400:
            detail = self._extract_detail(response)
            code = response.status_code if response.status_code < 500 else 503
            raise HTTPException(status_code=code, detail=detail)

        if not response.content:
            return {}

        try:
            return response.json()
        except Exception:  # noqa: BLE001
            return {"raw": response.text}

    @staticmethod
    def _extract_detail(response: httpx.Response) -> Any:
        try:
            body = response.json()
            if isinstance(body, dict) and "detail" in body:
                return body["detail"]
            return body
        except Exception:  # noqa: BLE001
            return response.text or "Agent service error"


agent_gateway = AgentGateway()
