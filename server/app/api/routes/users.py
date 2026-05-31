from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.app.db.database import get_db
from server.app.models.user import User
from server.app.schemas.user_schema import UserCreate, UserResponse
from server.app.core.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"] 
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """

    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    hashed_pwd = hash_password(user_in.password)

    db_user = User(
        email=user_in.email,
        nickname=user_in.nickname,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        base_currency=user_in.base_currency,
        hashed_password=hashed_pwd
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user) 

    return db_user