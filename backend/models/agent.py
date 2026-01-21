from datetime import datetime
from typing import List, Dict, Any, Optional, Annotated
from bson import ObjectId
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler
    ) -> core_schema.CoreSchema:
        def validate(value):
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return ObjectId(value)
                raise ValueError("Invalid ObjectId string")
            raise ValueError("Invalid ObjectId")
        
        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.str_schema(),
            serialization=core_schema.str_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema, handler
    ) -> JsonSchemaValue:
        return {"type": "string"}


class AgentBase(BaseModel):
    id: str  # Agent identifier (e.g., "codecraft")
    name: str
    description: str
    icon: str
    category: str
    features: List[str]
    system_prompt: str
    gemini_config: Dict[str, Any] = {}


class AgentInDB(AgentBase):
    _id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class Agent(AgentBase):
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
