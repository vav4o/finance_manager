from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import calendar
from datetime import datetime, date

from server.app.db.database import get_db
from server.app.models.budget import Budget
from server.app.models.transaction import Transaction
from server.app.models.category import Category, CategoryType
from server.app.schemas.budget_schema import BudgetCreate, BudgetResponse
from server.app.api.dependencies import get_current_user
from server.app.models.user import User

router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)

@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(budget_in: BudgetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new budget
    """ 
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_in.category_id,
        Budget.month == budget_in.month,
        Budget.year == budget_in.year
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Budget for this category and month already exists.")

    db_budget = Budget(
        user_id=current_user.id,
        category_id=budget_in.category_id,
        amount=budget_in.amount,
        month=budget_in.month,
        year=budget_in.year
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/", response_model=List[BudgetResponse])
def get_budgets(month: int, year: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns the budgets for the selected period
    """
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == month,
        Budget.year == year
    ).all()

    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day, 23, 59, 59)

    for budget in budgets:
        query = db.query(func.sum(Transaction.amount)).join(Category).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Category.type == CategoryType.EXPENSE
        )
        
        if budget.category_id:
            query = query.filter(Transaction.category_id == budget.category_id)

        spent = query.scalar()
        budget.spent_amount = spent if spent else 0.0

    return budgets

@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int, 
    budget_in: BudgetCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Едит a бъджет
    """
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found.")
        
    if db_budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this budget.")

    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_in.category_id,
        Budget.month == budget_in.month,
        Budget.year == budget_in.year,
        Budget.id != budget_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="You already have another budget set for this category in this period."
        )

    db_budget.category_id = budget_in.category_id
    db_budget.amount = budget_in.amount
    db_budget.month = budget_in.month
    db_budget.year = budget_in.year

    db.commit()
    db.refresh(db_budget)
    
    db_budget.spent_amount = 0.0 
    
    return db_budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Delete a budget.
    """
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found.")

    if db_budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this budget.")

    db.delete(db_budget)
    db.commit()
    return None