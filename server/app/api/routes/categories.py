from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, cast
from server.app.db.database import get_db
from server.app.models.category import Category
from server.app.schemas.category_schema import CategoryCreate, CategoryResponse
from server.app.api.dependencies import get_current_user
from server.app.models.user import User, UserRole

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new category.
    If created by an admin, it will be a global one
    """
    
    user_id = None if cast(UserRole, current_user.role) == UserRole.ADMIN else cast(int, current_user.id)

    db_category = Category(
        user_id=user_id,
        name=category_in.name,
        type=category_in.type,
        icon_color=category_in.icon_color
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryResponse])
def get_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns all categories: user's and global
    """
    categories = db.query(Category).filter(
        or_(
            Category.user_id == None,
            Category.user_id == cast(int, current_user.id)
        )
    ).all()
    return categories

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Deletes a category.
    The admins delete global ones.
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found.")

    if cast(UserRole, current_user.role) == UserRole.ADMIN:
        if db_category.user_id is not None:
            raise HTTPException(status_code=403, detail="Admins can only delete global categories.")
    elif cast(int, db_category.user_id) != cast(int, current_user.id):
        raise HTTPException(status_code=403, detail="You are not authorized to delete this category.")
        
    db.delete(db_category)
    db.commit()
    return None