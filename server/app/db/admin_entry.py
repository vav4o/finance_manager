from sqlalchemy.orm import Session
from server.app.models.user import User, UserRole
from server.app.core.security import hash_password, settings

def add_admin_user(db: Session):
    ADMIN_EMAIL = "admin@admin.com"
    ADMIN_PASSWORD = settings.admin_password

    if not ADMIN_PASSWORD:
        raise RuntimeError("ADMIN_PASSWORD is missing from server/.env")
    
    existing_admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    
    if not existing_admin:       
        db_admin = User(
            username="admin",
            email="admin@admin.com",
            hashed_password=hash_password(ADMIN_PASSWORD),
            first_name="Admin",
            last_name="Admin",
            base_currency="EUR",
            role=UserRole.ADMIN,
            is_blocked=False,
            avatar=""
        )
        
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)