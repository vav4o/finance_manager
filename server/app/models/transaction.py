from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from server.app.db.database import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    is_recurring = Column(Boolean, default=False)
    next_recurring_date = Column(DateTime, nullable=True)

    user = relationship("User")
    account = relationship("Account")
    category = relationship("Category")