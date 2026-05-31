from pydantic import BaseModel, Field
from typing import Optional
from server.app.models.user import UserRole


class UserBase(BaseModel):
    email: str = Field(
        ...,
        min_length=2,
        max_length=50,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    nickname: str = Field(..., min_length=2, max_length=50)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: Optional[str] = None
    base_currency: str = Field(default="BGN", min_length=3, max_length=3)

class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=8,
        max_length=50, 
        description="Password must be at least 8 characters long.")


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_blocked: bool

    class Config:
        from_attributes = True