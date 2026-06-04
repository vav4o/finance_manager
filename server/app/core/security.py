from datetime import datetime, timedelta
from pathlib import Path

from jose import jwt
from passlib.context import CryptContext
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    secret_key: str = Field(default="", validation_alias="SECRET_KEY")
    admin_password: str = Field(default="", validation_alias="ADMIN_PASSWORD")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = SecuritySettings()

if not settings.secret_key:
    raise RuntimeError("SECRET_KEY is missing from server/.env")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt