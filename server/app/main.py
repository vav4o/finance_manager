from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .db.database import engine, Base, get_db


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Finance Manager API",
    description="Backend API for the project Personal Finance Manager.",
    version="1.0.0"
)


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