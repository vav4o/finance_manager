from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from server.app.schemas.account_schema import AccountResponse
from server.app.schemas.category_schema import CategoryResponse

class TransactionBase(BaseModel):
    account_id: int
    category_id: int
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    currency: str = Field(default="BGN", min_length=3, max_length=3)
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    description: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None
    is_recurring: bool = False

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    account: Optional[AccountResponse] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True