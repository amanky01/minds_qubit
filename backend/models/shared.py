"""
Shared Pydantic types used across multiple models.

Keeping PyObjectId here eliminates the copy-paste that existed in every
model file and is the single source of truth for BSON ↔ Pydantic bridging.
"""

from __future__ import annotations

from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """Pydantic-compatible wrapper around bson.ObjectId."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: object,
        handler: object,
    ) -> core_schema.CoreSchema:
        def validate(value: object) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return ObjectId(value)
                raise ValueError(f"Invalid ObjectId string: {value!r}")
            raise ValueError(f"Cannot coerce {type(value)} to ObjectId")

        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.str_schema(),
            serialization=core_schema.str_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: object,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return {"type": "string"}
