from typing import Optional, Dict
from core.database import get_database
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from models.user import UserInDB, UserCreate, User
from datetime import datetime, timedelta
from bson import ObjectId
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    async def register_user(self, user_data: UserCreate) -> Dict:
        """Register a new user"""
        try:
            db = get_database()
        except ConnectionError as e:
            raise ValueError("Database connection error. Please ensure MongoDB is running.")
        
        users_collection = db["users"]
        
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = UserInDB(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        result = await users_collection.insert_one(user.dict(by_alias=True))
        user_id = str(result.inserted_id)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user_id, "email": user_data.email})
        refresh_token = create_refresh_token(data={"sub": user_id, "email": user_data.email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "is_active": True
            }
        }
    
    async def login_user(self, email: str, password: str) -> Dict:
        """Login user and return tokens"""
        try:
            db = get_database()
        except ConnectionError as e:
            raise ValueError("Database connection error. Please ensure MongoDB is running.")
        
        users_collection = db["users"]
        
        # Find user
        user_doc = await users_collection.find_one({"email": email})
        if not user_doc:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user_doc["hashed_password"]):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user_doc.get("is_active", True):
            raise ValueError("User account is inactive")
        
        user_id = str(user_doc["_id"])
        
        # Create tokens
        access_token = create_access_token(data={"sub": user_id, "email": email})
        refresh_token = create_refresh_token(data={"sub": user_id, "email": email})
        
        # Update last login
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "full_name": user_doc.get("full_name"),
                "is_active": user_doc.get("is_active", True)
            }
        }
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token"""
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise ValueError("Invalid token payload")
        
        # Verify user still exists and is active
        try:
            db = get_database()
        except ConnectionError as e:
            raise ValueError("Database connection error. Please ensure MongoDB is running.")
        
        users_collection = db["users"]
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc or not user_doc.get("is_active", True):
            raise ValueError("User not found or inactive")
        
        # Create new access token
        access_token = create_access_token(data={"sub": user_id, "email": email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def get_current_user(self, user_id: str) -> Dict:
        """Get current user information"""
        try:
            db = get_database()
        except ConnectionError as e:
            raise ValueError("Database connection error. Please ensure MongoDB is running.")
        
        users_collection = db["users"]
        
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise ValueError("User not found")
        
        return {
            "id": str(user_doc["_id"]),
            "email": user_doc["email"],
            "full_name": user_doc.get("full_name"),
            "is_active": user_doc.get("is_active", True)
        }
    
    async def oauth_login(self, provider: str, provider_user_id: str, email: str, name: Optional[str] = None) -> Dict:
        """Login or register user via OAuth"""
        try:
            db = get_database()
        except ConnectionError as e:
            raise ValueError("Database connection error. Please ensure MongoDB is running.")
        
        users_collection = db["users"]
        
        # Check if user exists with this OAuth provider
        user_doc = await users_collection.find_one({
            f"oauth_providers.{provider}": provider_user_id
        })
        
        if not user_doc:
            # Check if user exists with this email
            user_doc = await users_collection.find_one({"email": email})
            
            if user_doc:
                # Link OAuth provider to existing account
                oauth_providers = user_doc.get("oauth_providers", {})
                oauth_providers[provider] = provider_user_id
                await users_collection.update_one(
                    {"_id": user_doc["_id"]},
                    {"$set": {"oauth_providers": oauth_providers, "updated_at": datetime.utcnow()}}
                )
            else:
                # Create new user
                user = UserInDB(
                    email=email,
                    hashed_password="",  # OAuth users don't have passwords
                    full_name=name,
                    oauth_providers={provider: provider_user_id}
                )
                result = await users_collection.insert_one(user.dict(by_alias=True))
                user_doc = await users_collection.find_one({"_id": result.inserted_id})
        
        user_id = str(user_doc["_id"])
        
        # Create tokens
        access_token = create_access_token(data={"sub": user_id, "email": email})
        refresh_token = create_refresh_token(data={"sub": user_id, "email": email})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "full_name": user_doc.get("full_name"),
                "is_active": user_doc.get("is_active", True)
            }
        }


# Global instance
auth_service = AuthService()
