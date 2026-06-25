from pydantic import BaseModel, Field

from schemas.base import BaseSchema


class UserResponse(BaseSchema):
    id: int
    username: str
    nickname: str
    pin_changed: bool
    created_at: int
    updated_at: int


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
