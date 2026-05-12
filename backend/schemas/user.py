from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    created_at: int
    updated_at: int

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    password: str | None = Field(default=None, min_length=6, max_length=64)
    old_password: str | None = None
