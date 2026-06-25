from pydantic import BaseModel, Field

from schemas.base import BaseSchema


class LoginRequest(BaseModel):
    username: str
    pin: str = Field(min_length=4, max_length=6)


class SecurityVerifyRequest(BaseModel):
    username: str
    answer: str


class ResetPinRequest(BaseModel):
    username: str
    answer: str
    new_pin: str = Field(min_length=4, max_length=6)


class ChangePinRequest(BaseModel):
    current_pin: str = Field(min_length=4, max_length=6)
    new_pin: str = Field(min_length=4, max_length=6)


class AuthResponse(BaseSchema):
    user: "UserResponse"
    must_change_pin: bool = False


class SecurityQuestionResponse(BaseSchema):
    question: str


from schemas.user import UserResponse  # noqa: E402
