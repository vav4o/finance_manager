from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from server.app.db.database import Base
import enum

class AccountType(str, enum.Enum):
    CASH = "cash"
    BANK = "bank"
    CARD = "card"
    SAVINGS = "savings"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), default=AccountType.CASH)
    currency = Column(String, default="BGN")
    balance = Column(Float, default=0.0)

    user = relationship("User")