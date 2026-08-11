from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User

pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def hash_password(value: str) -> str:
    return pwd.hash(value)


def verify_password(value: str, hashed: str) -> bool:
    return pwd.verify(value, hashed)


def create_token(username: str) -> str:
    payload = {"sub": username, "exp": datetime.now(timezone.utc) + timedelta(hours=8)}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    try:
        username = jwt.decode(token, settings.secret_key, algorithms=["HS256"])["sub"]
    except (JWTError, KeyError):
        raise HTTPException(401, "登录凭证无效", headers={"WWW-Authenticate": "Bearer"})
    user = db.scalar(select(User).where(User.username == username, User.enabled.is_(True)))
    if not user:
        raise HTTPException(401, "用户不存在或已禁用")
    return user
