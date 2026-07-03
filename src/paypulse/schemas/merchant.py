from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreate(BaseModel):
    name: str
    is_live: bool = False


class ApiKeyResponse(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreatedResponse(ApiKeyResponse):
    key: str
