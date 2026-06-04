from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./finance_manager.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_extra_columns():
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "users" in tables:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "avatar" not in user_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR"))

    if "categories" in tables:
        category_columns = {column["name"] for column in inspector.get_columns("categories")}
        if "icon" not in category_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE categories ADD COLUMN icon VARCHAR"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
