from sqlalchemy import Column, Integer, String, Boolean, Enum
from server.app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    base_currency = Column(String, default="BGN")
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_blocked = Column(Boolean, default=False)