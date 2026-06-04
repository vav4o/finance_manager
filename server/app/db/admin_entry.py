from sqlalchemy.orm import Session
from server.app.models.user import User, UserRole
from server.app.core.security import hash_password, settings

def add_admin_user(db: Session):
    admin_username = "admin"
    admin_email = "admin@admin.com"
    admin_password = settings.admin_password

    if not admin_password:
        raise RuntimeError("ADMIN_PASSWORD is missing from server/.env")

    admin_user = db.query(User).filter(User.username == admin_username).first()
    if not admin_user:
        admin_user = db.query(User).filter(User.email == admin_email).first()

    if not admin_user:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            first_name="Admin",
            last_name="Admin",
            base_currency="EUR",
            is_blocked=False,
            avatar="",
        )
        db.add(admin_user)

    admin_user.username = admin_username
    admin_user.email = admin_email
    admin_user.hashed_password = hash_password(admin_password)
    admin_user.role = UserRole.ADMIN
    admin_user.is_blocked = False

    db.commit()
    db.refresh(admin_user)
