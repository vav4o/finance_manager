from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import cast
from sqlalchemy.orm import Session
from server.app.db.database import get_db
from server.app.models.user import User
from server.app.schemas.user_schema import UserCreate, UserResponse
from server.app.core.security import hash_password, verify_password, create_access_token
from server.app.api.dependencies import get_current_user
from server.app.core.services import check_and_process_recurring

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

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login a user. Returns a JWT token.
    """
    # Named usernames "nickname"... should fix this at some point TODO: VN
    user = db.query(User).filter(User.nickname == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, cast(str, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    check_and_process_recurring(user_id=user.id, db=db)
    
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently logged-in user.
    Requires a valid JWT token (via get_current_user).
    """
    return current_user