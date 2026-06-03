from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from server.app.db.database import Base
import enum

class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

#Empty user_id means global category
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    color = Column(String, nullable=True)
    icon = Column(String, nullable=True)

    user = relationship("User")