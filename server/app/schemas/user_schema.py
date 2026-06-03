from pydantic import BaseModel, Field, field_validator
from typing import Optional
from server.app.models.user import UserRole


class UserBase(BaseModel):
    email: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    username: str = Field(..., min_length=2, max_length=50)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: Optional[str] = None
    base_currency: str = Field(default="EUR", min_length=3, max_length=3)

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        return value


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_blocked: bool

    class Config:
        from_attributes = True