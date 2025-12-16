# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UserCreate, UserResponse, Token
from ..crud import get_user_by_email, create_user
from ..auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
    set_refresh_token_cookie,
    get_refresh_token_from_cookie,
    verify_token
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@router.post("/login", response_model=Token)
def login(response: Response, user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)}, db=db)
    set_refresh_token_cookie(response, refresh_token)
    
    return {"access_token": access_token}

@router.post("/refresh", response_model=Token)
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    refresh_token = get_refresh_token_from_cookie(request)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    payload = verify_token(refresh_token, db, "refresh")
    user_id = payload["user_id"]
    
    # Issue new tokens
    access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user_id)}, db=db)
    set_refresh_token_cookie(response, new_refresh_token)
    
    return {"access_token": access_token}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"msg": "Logged out"}