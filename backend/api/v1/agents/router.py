from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from api.v1.agents.schemas import (
    AgentResponse,
    AgentExecuteRequest,
    AgentExecuteResponse,
    ConversationResponse
)
from api.v1.agents.service import agent_service
from core.dependencies import get_current_user, get_optional_current_user
from typing import Dict

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    category: Optional[str] = None,
    current_user: Optional[Dict] = Depends(get_optional_current_user)
):
    """List all available agents (public endpoint)"""
    try:
        if category:
            agents = await agent_service.get_agents_by_category(category)
        else:
            agents = await agent_service.get_all_agents()
        
        return [
            AgentResponse(
                id=agent.id,
                name=agent.name,
                description=agent.description,
                icon=agent.icon,
                category=agent.category,
                features=agent.features
            )
            for agent in agents
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agents: {str(e)}"
        )


@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get all agent categories"""
    try:
        categories = await agent_service.get_all_categories()
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent details by ID"""
    try:
        agent = await agent_service.get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            icon=agent.icon,
            category=agent.category,
            features=agent.features
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching agent: {str(e)}"
        )


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Execute/chat with an agent (requires authentication)"""
    try:
        result = await agent_service.execute_agent(
            agent_id=agent_id,
            user_message=request.message,
            user_id=current_user["user_id"],
            conversation_id=request.conversation_id
        )
        
        return AgentExecuteResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            agent_id=result["agent_id"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing agent: {str(e)}"
        )


@router.get("/{agent_id}/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    agent_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's conversation history with an agent"""
    try:
        conversations = await agent_service.get_user_conversations(
            user_id=current_user["user_id"],
            agent_id=agent_id
        )
        
        return [
            ConversationResponse(**conv)
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )
