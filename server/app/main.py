from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from server.app.api.routes import users, accounts, categories, transactions, budgets, admin
from server.app.db.database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Finance Manager API",
    description="Backend API for the project Personal Finance Manager.",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {
        "message": "Test endpoint working!",
        "docs": "/docs"
    }

@app.get("/healthcheck")
def health_check(db: Session = Depends(get_db)):
    try:
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}