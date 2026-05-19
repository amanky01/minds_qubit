"""
HTTP gateway from MindsQubit core to agent microservices.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status

from core.config import settings
from services.agent_catalog import AgentDefinition, get_agent

logger = logging.getLogger(__name__)

HEADER_SERVICE_KEY = "X-Service-Key"
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
        if settings.AGENT_SERVICE_API_KEY:
            headers[HEADER_SERVICE_KEY] = settings.AGENT_SERVICE_API_KEY
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

    async def execute(
        self,
        agent_id: str,
        user_id: str,
        email: str,
        plan_id: str,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        agent = self._agent(agent_id)
        if agent.agent_type != "chat":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent '{agent_id}' does not support chat execution",
            )

        url = f"{agent.service_url.rstrip('/')}/v1/execute"
        payload = {"message": message, "conversation_id": conversation_id}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    url,
                    json=payload,
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

        data = response.json()
        return {
            "response": data["response"],
            "conversation_id": data["conversation_id"],
            "agent_id": data.get("agent_id", agent_id),
        }

    async def get_user_conversations(
        self,
        agent_id: str,
        user_id: str,
        email: str,
        plan_id: str,
    ) -> List[dict]:
        agent = self._agent(agent_id)
        if agent.agent_type != "chat":
            return []

        url = f"{agent.service_url.rstrip('/')}/v1/conversations"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(
                    url,
                    params={"user_id": user_id},
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
            raise HTTPException(status_code=response.status_code, detail=detail)

        return response.json()

    async def proxy_integration(
        self,
        agent_id: str,
        method: str,
        path: str,
        user_id: str,
        email: str,
        plan_id: str,
        json_body: Optional[dict] = None,
    ) -> Any:
        agent = self._agent(agent_id)
        url = f"{agent.service_url.rstrip('/')}{path}"

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.request(
                    method,
                    url,
                    json=json_body,
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
            raise HTTPException(status_code=response.status_code, detail=detail)

        return response.json()

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
