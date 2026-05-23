from __future__ import annotations

import os
from typing import List, Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from agent_contract.headers import HEADER_PLAN_ID, HEADER_USER_EMAIL, HEADER_USER_ID
from agent_contract.schemas import SubscribeRequest, SubscribeResponse, UnsubscribeRequest

ALLOWED_NOTIFICATION_CATEGORIES = {"daily_digest", "instant_alert"}
ALLOWED_OPPORTUNITY_TYPES = {"internship", "job", "hackathon", "research", "all"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPPORTUNITY_CRAWLER_URL: str = "https://opportunity-crawler.onrender.com"
    HOST: str = "0.0.0.0"
    PORT: int = 8017


settings = Settings()


def require_service(
    x_user_id: Optional[str] = Header(None, alias=HEADER_USER_ID),
    x_user_email: Optional[str] = Header(None, alias=HEADER_USER_EMAIL),
    x_plan_id: Optional[str] = Header(None, alias=HEADER_PLAN_ID),
) -> dict:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing user context")
    return {
        "user_id": x_user_id,
        "email": x_user_email or "",
        "plan_id": x_plan_id or "free",
    }


def _validate_subscribe(body: SubscribeRequest) -> None:
    cats = set(body.notification_categories)
    types = set(body.opportunity_types)
    if not cats.issubset(ALLOWED_NOTIFICATION_CATEGORIES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"notification_categories must be subset of {sorted(ALLOWED_NOTIFICATION_CATEGORIES)}",
        )
    if not types.issubset(ALLOWED_OPPORTUNITY_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"opportunity_types must be subset of {sorted(ALLOWED_OPPORTUNITY_TYPES)}",
        )


async def _proxy(method: str, path: str, json_body: dict) -> dict:
    base = settings.OPPORTUNITY_CRAWLER_URL.rstrip("/")
    url = f"{base}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(method, url, json=json_body)
    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json()
        except Exception:  # noqa: BLE001
            pass
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


app = FastAPI(title="MindsQubit Agent — OpportunityAlert", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok", "agent_id": "opportunityalert"}


@app.post("/v1/subscribe", response_model=SubscribeResponse)
async def subscribe(
    body: SubscribeRequest,
    _user: dict = Depends(require_service),
) -> SubscribeResponse:
    _validate_subscribe(body)
    data = await _proxy("POST", "/subscribe", body.model_dump(mode="json"))
    return SubscribeResponse(**data)


@app.patch("/v1/subscribe", response_model=SubscribeResponse)
async def update_subscription(
    body: SubscribeRequest,
    _user: dict = Depends(require_service),
) -> SubscribeResponse:
    _validate_subscribe(body)
    data = await _proxy("PATCH", "/subscribe", body.model_dump(mode="json"))
    return SubscribeResponse(**data)


@app.post("/v1/unsubscribe")
async def unsubscribe(
    body: UnsubscribeRequest,
    _user: dict = Depends(require_service),
) -> dict:
    return await _proxy("POST", "/subscribe/unsubscribe", body.model_dump(mode="json"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
