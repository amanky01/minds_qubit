"""Request/response models for OpportunityAlert subscription routes."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, EmailStr, Field


class OpportunitySubscribeRequest(BaseModel):
    email: EmailStr
    notification_categories: List[str] = Field(..., min_length=1)
    opportunity_types: List[str] = Field(..., min_length=1)


class OpportunitySubscribeResponse(BaseModel):
    email: str
    status: str
    subscriber: Dict[str, Any]


class OpportunityUnsubscribeRequest(BaseModel):
    email: EmailStr
