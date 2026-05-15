from fastapi import APIRouter

from api.v1.agents.router import router as agents_router
from api.v1.auth.router import router as auth_router
from api.v1.quota.router import router as quota_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(agents_router)
router.include_router(quota_router)

