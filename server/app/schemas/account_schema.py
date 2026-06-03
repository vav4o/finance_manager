from pydantic import BaseModel, Field
from server.app.models.account import AccountType

class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: AccountType
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    balance: float = 0.0

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True