"""
Authentication service.

Handles:  register · login · token refresh · get-me · OAuth (Google / GitHub)

All DB access goes through db_manager.central so this service never needs
to know the physical collection location.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Optional

from bson import ObjectId

from core.config import settings
from core.database import db_manager
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from models.user import UserCreate, UserInDB

logger = logging.getLogger(__name__)

# Convenience alias
_users = lambda: db_manager.central["users"]  # noqa: E731


def _user_response(doc: dict) -> dict:
    """Build the public user dict returned in all auth responses."""
    return {
        "id":        str(doc["_id"]),
        "email":     doc["email"],
        "full_name": doc.get("full_name"),
        "plan_id":   doc.get("plan_id", "free"),
        "is_active": doc.get("is_active", True),
    }


class AuthService:

    # ── Register ───────────────────────────────────────────────────────────

    async def register_user(self, user_data: UserCreate) -> Dict:
        col = _users()
        if await col.find_one({"email": user_data.email}):
            raise ValueError("An account with this email already exists.")

        user = UserInDB(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            plan_id=settings.DEFAULT_PLAN_ID,
        )
        result = await col.insert_one(user.model_dump(by_alias=True))
        user_id = str(result.inserted_id)

        return {
            **self._make_tokens(user_id, user_data.email),
            "user": {
                "id":        user_id,
                "email":     user_data.email,
                "full_name": user_data.full_name,
                "plan_id":   settings.DEFAULT_PLAN_ID,
                "is_active": True,
            },
        }

    # ── Login ──────────────────────────────────────────────────────────────

    async def login_user(self, email: str, password: str) -> Dict:
        col = _users()
        doc = await col.find_one({"email": email})

        # Use the same error message for missing user and wrong password
        # to avoid email enumeration.
        if not doc or not verify_password(password, doc.get("hashed_password", "")):
            raise ValueError("Invalid email or password.")

        if not doc.get("is_active", True):
            raise ValueError("This account has been deactivated.")

        user_id = str(doc["_id"])
        await col.update_one(
            {"_id": doc["_id"]},
            {"$set": {"updated_at": datetime.utcnow()}},
        )

        return {**self._make_tokens(user_id, email), "user": _user_response(doc)}

    # ── Token refresh ──────────────────────────────────────────────────────

    async def refresh_access_token(self, refresh_token: str) -> Dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid or expired refresh token.")

        user_id: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")
        if not user_id or not email:
            raise ValueError("Malformed token payload.")

        doc = await _users().find_one({"_id": ObjectId(user_id)})
        if not doc or not doc.get("is_active", True):
            raise ValueError("User not found or account deactivated.")

        access_token = create_access_token({"sub": user_id, "email": email})
        return {"access_token": access_token, "token_type": "bearer"}

    # ── Get current user ───────────────────────────────────────────────────

    async def get_current_user(self, user_id: str) -> Dict:
        doc = await _users().find_one({"_id": ObjectId(user_id)})
        if not doc:
            raise ValueError("User not found.")
        return _user_response(doc)

    # ── OAuth ──────────────────────────────────────────────────────────────

    async def oauth_login(
        self,
        provider: str,
        provider_user_id: str,
        email: str,
        name: Optional[str] = None,
    ) -> Dict:
        """Find-or-create a user via OAuth, then return tokens."""
        col = _users()

        # 1. Try matching by OAuth provider ID
        doc = await col.find_one({f"oauth_providers.{provider}": provider_user_id})

        if not doc:
            # 2. Try matching by email (link provider to existing account)
            doc = await col.find_one({"email": email})
            if doc:
                await col.update_one(
                    {"_id": doc["_id"]},
                    {
                        "$set": {
                            f"oauth_providers.{provider}": provider_user_id,
                            "updated_at": datetime.utcnow(),
                        }
                    },
                )
            else:
                # 3. Create new user
                user = UserInDB(
                    email=email,
                    hashed_password="",       # OAuth users have no password
                    full_name=name,
                    oauth_providers={provider: provider_user_id},
                    plan_id=settings.DEFAULT_PLAN_ID,
                )
                result = await col.insert_one(user.model_dump(by_alias=True))
                doc = await col.find_one({"_id": result.inserted_id})

        user_id = str(doc["_id"])
        return {**self._make_tokens(user_id, email), "user": _user_response(doc)}

    # ── Internal helpers ───────────────────────────────────────────────────

    @staticmethod
    def _make_tokens(user_id: str, email: str) -> Dict:
        payload = {"sub": user_id, "email": email}
        return {
            "access_token":  create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type":    "bearer",
        }


# Module-level singleton
auth_service = AuthService()
