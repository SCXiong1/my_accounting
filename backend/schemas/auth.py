from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=32)
    email: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=6, max_length=64)
    nickname: str = Field(default="", max_length=64)


class LoginRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    username: str
    email: str
    new_password: str = Field(min_length=6, max_length=64)


class AuthResponse(BaseModel):
    token: str
    user: "UserResponse"

    model_config = {"from_attributes": True}


from schemas.user import UserResponse
