from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class WebhookCreate(BaseModel):
    url: HttpUrl
    events: list[str]


class WebhookResponse(BaseModel):
    id: UUID
    url: str
    secret: str
    events: list[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
