from __future__ import annotations

from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status

from agent_contract.headers import HEADER_PLAN_ID, HEADER_USER_EMAIL, HEADER_USER_ID
from agent_contract.schemas import ConversationListItem, ExecuteRequest, ExecuteResponse

from chat_runtime.agent_config import ChatAgentConfig
from chat_runtime.auth import ServiceUserContext, verify_service_request
from chat_runtime.database import agent_db
from chat_runtime.executor import ChatExecutor
from chat_runtime.gemini_service import GeminiService
from chat_runtime.settings import Settings


def create_chat_app(agent_config: ChatAgentConfig) -> FastAPI:
    settings = Settings(AGENT_ID=agent_config.id)
    gemini = GeminiService(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
    executor = ChatExecutor(
        agent_id=agent_config.id,
        system_prompt=agent_config.system_prompt,
        gemini_config=agent_config.gemini_config,
        gemini=gemini,
    )

    def require_user(
        x_user_id: Optional[str] = Header(None, alias=HEADER_USER_ID),
        x_user_email: Optional[str] = Header(None, alias=HEADER_USER_EMAIL),
        x_plan_id: Optional[str] = Header(None, alias=HEADER_PLAN_ID),
    ) -> ServiceUserContext:
        return verify_service_request(x_user_id, x_user_email, x_plan_id)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await agent_db.connect(settings)
        yield
        await agent_db.disconnect()

    app = FastAPI(
        title=f"MindsQubit Agent — {agent_config.name}",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "agent_id": agent_config.id}

    @app.post("/v1/execute", response_model=ExecuteResponse)
    async def execute(
        body: ExecuteRequest,
        user: ServiceUserContext = Depends(require_user),
    ) -> ExecuteResponse:
        try:
            return await executor.execute(user, body.message, body.conversation_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

    @app.get("/v1/conversations", response_model=List[ConversationListItem])
    async def list_conversations(
        user_id: str = Query(...),
        user: ServiceUserContext = Depends(require_user),
    ) -> List[ConversationListItem]:
        if user_id != user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        rows = await executor.list_conversations(user_id)
        return [ConversationListItem(**row) for row in rows]

    return app
