from pydantic import BaseModel, Field
from typing import Optional
from server.app.models.category import CategoryType

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: CategoryType
    color: Optional[str] = None
    icon: Optional[str] = Field(None)

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
        