from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from server.app.db.database import get_db
from server.app.models.user import User
from server.app.models.transaction import Transaction
from server.app.schemas.user_schema import UserResponse
from server.app.api.dependencies import get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin)] 
)

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """
    Get all users
    """
    users = db.query(User).all()
    return users

@router.put("/users/{user_id}/block", response_model=UserResponse)
def toggle_block_user(user_id: int, db: Session = Depends(get_db)):
    """
    Block/unblock a user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user.is_blocked = not user.is_blocked
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/statistics")
def get_system_statistics(db: Session = Depends(get_db)):
    """
    Get system statistics
    """
    total_users = db.query(User).count()
    blocked_users = db.query(User).filter(User.is_blocked == True).count()
    active_users = total_users - blocked_users
    
    total_transactions = db.query(Transaction).count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "blocked": blocked_users
        },
        "transactions": {
            "total_registered": total_transactions
        }
    }