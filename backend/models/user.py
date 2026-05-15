"""
User domain models.

UserInDB   → stored in central DB → users collection
UserCreate → request body for registration
User       → public-facing API response (no password hash)
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Dict, Optional

from pydantic import BaseModel, EmailStr, Field

from models.shared import PyObjectId


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    """MongoDB document shape for the users collection."""
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    hashed_password: str
    # Social login providers  e.g.  {"google": "<google_sub>", "github": "123"}
    oauth_providers: Dict[str, str] = Field(default_factory=dict)
    # Subscription plan: 'free' | 'pro' | 'enterprise'
    plan_id: str = "free"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class User(UserBase):
    """Public-facing user representation (never exposes hashed_password)."""
    id: str
    plan_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
