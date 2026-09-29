from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.account import AccountSummaryResponse
from app.schemas.base import BaseSchema


class UserRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Password cannot be empty")
        return cleaned


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserPublicResponse(BaseSchema):
    id: int
    name: str
    email: str
    created_at: datetime


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseSchema):
    user: UserPublicResponse
    account: AccountSummaryResponse
    access_token: str
    token_type: str = "bearer"
