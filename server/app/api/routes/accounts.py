from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, cast, Any
from server.app.db.database import get_db
from server.app.models.account import Account
from server.app.schemas.account_schema import AccountCreate, AccountResponse
from server.app.api.dependencies import get_current_user
from server.app.models.user import User

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account_in: AccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create new account for the current user.
    """
    db_account = Account(
        user_id=cast(int, current_user.id),
        name=account_in.name,
        type=account_in.type,
        currency=account_in.currency,
        balance=account_in.balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/", response_model=List[AccountResponse])
def get_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns user's accounts.
    """
    accounts = db.query(Account).filter(Account.user_id == cast(int, current_user.id)).all()
    return accounts

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account_in: AccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Updates an account if it belongs to the current user.
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found.")
        
    if cast(int, db_account.user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this account.")
        
    cast(Any, db_account).name = account_in.name
    cast(Any, db_account).type = account_in.type
    cast(Any, db_account).currency = account_in.currency
    cast(Any, db_account).balance = account_in.balance
    
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Deletes an account if it belongs to the current user.
    """
    db_account = db.query(Account).filter(Account.id == account_id).first()
    
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found.")
        
    if cast(int, db_account.user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this account.")
        
    db.delete(db_account)
    db.commit()
    return None