from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from sqlalchemy import func
from typing import cast, List, Optional
from datetime import datetime
import calendar

from server.app.db.database import get_db
from server.app.models.transaction import Transaction
from server.app.models.account import Account
from server.app.models.category import Category, CategoryType
from server.app.schemas.transaction_schema import TransactionCreate, TransactionResponse
from server.app.api.dependencies import get_current_user
from server.app.models.user import User
from server.app.models.budget import Budget

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_in: TransactionCreate, ignore_budget_limit: bool = Query(False),current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new transaction
    """
    
    account = db.query(Account).filter(Account.id == transaction_in.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found.")
    if cast(bool, account.user_id) != cast(bool, current_user.id):
        raise HTTPException(status_code=403, detail="You do not have access to this bank account.")

    category = db.query(Category).filter(
        Category.id == transaction_in.category_id,
        or_(Category.user_id == None, Category.user_id == current_user.id)
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")



    if category.type == CategoryType.EXPENSE and not ignore_budget_limit:
        t_month = transaction_in.date.month if transaction_in.date else datetime.utcnow().month
        t_year = transaction_in.date.year if transaction_in.date else datetime.utcnow().year

        budget = db.query(Budget).filter(
            Budget.user_id == current_user.id,
            Budget.month == t_month,
            Budget.year == t_year,
            or_(Budget.category_id == transaction_in.category_id, Budget.category_id == None)
        ).first()

        if budget:
            _, last_day = calendar.monthrange(t_year, t_month)
            start_date = datetime(t_year, t_month, 1)
            end_date = datetime(t_year, t_month, last_day, 23, 59, 59)
            
            spent_query = db.query(func.sum(Transaction.amount)).join(Category).filter(
                Transaction.user_id == current_user.id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Category.type == CategoryType.EXPENSE
            )
            if budget.category_id:
                spent_query = spent_query.filter(Transaction.category_id == budget.category_id)
                
            total_spent = spent_query.scalar() or 0.0
            
            if total_spent + transaction_in.amount > budget.amount:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error_code": "BUDGET_EXCEEDED",
                        "message": f"This transaction will exceed your monthly budget of {budget.amount} {account.currency}. Are you sure you want to save it?",
                        "current_spent": total_spent,
                        "budget_amount": budget.amount
                    }
                )


    db_transaction = Transaction(
        user_id=current_user.id,
        account_id=transaction_in.account_id,
        category_id=transaction_in.category_id,
        amount=transaction_in.amount,
        currency=transaction_in.currency,
        date=transaction_in.date,
        description=transaction_in.description,
        notes=transaction_in.notes,
        is_recurring=transaction_in.is_recurring
    )
    
    db.add(db_transaction)
    
    transaction_amount = float(transaction_in.amount)
    account_balance = float(account.balance)

    if cast(bool, category.type) == CategoryType.INCOME:
        setattr(account, "balance", account_balance + transaction_amount)
    elif cast(bool, category.type) == CategoryType.EXPENSE:
        setattr(account, "balance", account_balance - transaction_amount)
    
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[CategoryType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    
    search: Optional[str] = None,
    
    sort_by: str = Query("date"),
    sort_order: str = Query("desc"),
    
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns user's transactions (20 per page)
    """
    
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    if transaction_type:
        query = query.join(Category).filter(Category.type == transaction_type)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(search_filter),
                Transaction.notes.ilike(search_filter)
            )
        )

    order_func = desc if sort_order == "desc" else asc
    if sort_by == "amount":
        query = query.order_by(order_func(Transaction.amount))
    else:
        query = query.order_by(order_func(Transaction.date))

    transactions = query.offset(offset).limit(limit).all()
    
    return transactions

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Delete a transaction
    """

    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")
        
    if db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this transaction.")

    account = db.query(Account).filter(Account.id == db_transaction.account_id).first()
    category = db.query(Category).filter(Category.id == db_transaction.category_id).first()

    if account is not None and category is not None:
        transaction_amount = float(db_transaction.amount)
        account_balance = float(account.balance)

        if category.type == CategoryType.INCOME:
            setattr(account, "balance", account_balance - transaction_amount)
        elif category.type == CategoryType.EXPENSE:
            setattr(account, "balance", account_balance + transaction_amount)

        db.delete(db_transaction)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Account or category not found.")

    return None

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int, 
    transaction_in: TransactionCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Update a transaction
    """

    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    if db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this transaction.")

    old_account = db.query(Account).filter(Account.id == db_transaction.account_id).first()
    old_category = db.query(Category).filter(Category.id == db_transaction.category_id).first()

    new_account = db.query(Account).filter(Account.id == transaction_in.account_id).first()
    if not new_account or new_account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Invalid new account.")

    new_category = db.query(Category).filter(
        Category.id == transaction_in.category_id,
        or_(Category.user_id == None, Category.user_id == current_user.id)
    ).first()
    if not new_category:
        raise HTTPException(status_code=400, detail="Invalid new category.")

    if old_account is None or old_category is None:
        raise HTTPException(status_code=404, detail="Account or category not found.")

    old_transaction_amount = float(db_transaction.amount)
    old_account_balance = float(old_account.balance)

    if old_category.type == CategoryType.INCOME:
        setattr(old_account, "balance", old_account_balance - old_transaction_amount)
    elif old_category.type == CategoryType.EXPENSE:
        setattr(old_account, "balance", old_account_balance + old_transaction_amount)

    new_transaction_amount = float(transaction_in.amount)
    new_account_balance = float(new_account.balance)

    if new_category.type == CategoryType.INCOME:
        setattr(new_account, "balance", new_account_balance + new_transaction_amount)
    elif new_category.type == CategoryType.EXPENSE:
        setattr(new_account, "balance", new_account_balance - new_transaction_amount)

    db_transaction.account_id = transaction_in.account_id
    db_transaction.category_id = transaction_in.category_id
    db_transaction.amount = transaction_in.amount
    db_transaction.currency = transaction_in.currency
    db_transaction.date = transaction_in.date
    db_transaction.description = transaction_in.description
    db_transaction.notes = transaction_in.notes
    db_transaction.is_recurring = transaction_in.is_recurring

    db.commit()
    db.refresh(db_transaction)
    return db_transaction