from pydantic import BaseModel, Field
from typing import Optional
from server.app.schemas.category_schema import CategoryResponse

class BudgetBase(BaseModel):
    category_id: Optional[int] = Field(default=None, description="Leave empty for overall budget")
    amount: float = Field(..., gt=0, description="Budget limit")
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000)

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    category: Optional[CategoryResponse] = None
    
    spent_amount: float = 0.0 

    class Config:
        from_attributes = True