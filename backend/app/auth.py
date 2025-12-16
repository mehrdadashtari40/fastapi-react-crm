# app/auth.py
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Response, Request
from .database import SessionLocal
from .models import User, RefreshToken
from typing import Optional
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, db):
    from .crud import create_refresh_token as crud_create
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token = crud_create(db, user_id=data["sub"], expires_at=expire)
    return token.id

def verify_token(token: str, db, token_type: str = "access"):
    from .crud import get_refresh_token
    try:
        if token_type == "access":
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return {"user_id": int(user_id)}
        else:  # refresh token
            db_token = get_refresh_token(db, token)
            if not db_token or db_token.expires_at < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            return {"user_id": db_token.user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def set_refresh_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=True,          # HTTPS only (set to False in dev)
        samesite="lax",
        max_age=7 * 24 * 3600  # 7 days
    )

def get_refresh_token_from_cookie(request: Request):
    return request.cookies.get("refresh_token")