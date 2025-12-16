# app/deps.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .database import get_db
from .auth import verify_token
from .crud import get_user

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    payload = verify_token(token, db, "access")
    user = get_user(db, user_id=payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user