from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
import calendar
from server.app.models.transaction import Transaction
from server.app.models.account import Account
from server.app.models.category import Category, CategoryType

def add_months(sourcedate: datetime, months: int) -> datetime:
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day, sourcedate.hour, sourcedate.minute, sourcedate.second)

def check_and_process_recurring(user_id: int, db: Session):
    now = datetime.utcnow()
    
    due_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.is_recurring == True,
        or_(Transaction.next_recurring_date == None, Transaction.next_recurring_date <= now)
    ).all()

    for template in due_transactions:
        if template.next_recurring_date is None:
            template.next_recurring_date = add_months(template.date, 1)

        while template.next_recurring_date and template.next_recurring_date <= now:
            new_transaction = Transaction(
                user_id=template.user_id,
                account_id=template.account_id,
                category_id=template.category_id,
                amount=template.amount,
                currency=template.currency,
                date=template.next_recurring_date,
                description=f"{template.description} (Recurring)",
                notes=template.notes,
                is_recurring=False,
                next_recurring_date=None
            )
            db.add(new_transaction)

            account = db.query(Account).filter(Account.id == template.account_id).first()
            category = db.query(Category).filter(Category.id == template.category_id).first()

            if account and category:
                if category.type == CategoryType.INCOME:
                    account.balance += template.amount
                elif category.type == CategoryType.EXPENSE:
                    account.balance -= template.amount

            template.next_recurring_date = add_months(template.next_recurring_date, 1)
            
    db.commit()