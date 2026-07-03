from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    business_name: str
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ApiKeyInfo(BaseModel):
    id: UUID
    name: str
    key: str
    key_prefix: str
    is_live: bool


class RegisterResponse(BaseModel):
    id: UUID
    email: str
    business_name: str
    access_token: str
    api_keys: list[ApiKeyInfo]
    created_at: datetime

    model_config = {"from_attributes": True}


class MerchantResponse(BaseModel):
    id: UUID
    email: str
    business_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
