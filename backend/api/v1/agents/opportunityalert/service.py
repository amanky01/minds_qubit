"""OpportunityAlert integration — proxies subscribe APIs to the agent microservice."""

from __future__ import annotations

from services.agent_gateway import agent_gateway

AGENT_ID = "opportunityalert"


class OpportunityAlertService:
    async def subscribe(
        self,
        user_id: str,
        user_email: str,
        plan_id: str,
        body: dict,
    ) -> dict:
        return await agent_gateway.proxy_integration(
            agent_id=AGENT_ID,
            method="POST",
            path="/v1/subscribe",
            user_id=user_id,
            email=user_email,
            plan_id=plan_id,
            json_body=body,
        )

    async def update_subscription(
        self,
        user_id: str,
        user_email: str,
        plan_id: str,
        body: dict,
    ) -> dict:
        return await agent_gateway.proxy_integration(
            agent_id=AGENT_ID,
            method="PATCH",
            path="/v1/subscribe",
            user_id=user_id,
            email=user_email,
            plan_id=plan_id,
            json_body=body,
        )

    async def unsubscribe(
        self,
        user_id: str,
        user_email: str,
        plan_id: str,
        body: dict,
    ) -> dict:
        return await agent_gateway.proxy_integration(
            agent_id=AGENT_ID,
            method="POST",
            path="/v1/unsubscribe",
            user_id=user_id,
            email=user_email,
            plan_id=plan_id,
            json_body=body,
        )


opportunityalert_service = OpportunityAlertService()
