# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash
from datetime import datetime

def get_role_by_title(db: Session, title: str):
    return db.query(models.Role).filter(models.Role.title == title).first()

def create_default_roles(db: Session):
    roles = ["user", "admin"]
    for title in roles:
        if not get_role_by_title(db, title):
            role = models.Role(title=title)
            db.add(role)
    db.commit()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone_number == phone).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Ensure "user" role exists
    role = get_role_by_title(db, "user")
    if not role:
        raise Exception("Default role 'user' not found")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        email=user.email,
        hashed_password=hashed_password,
        role_id=role.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_refresh_token(db: Session, user_id: int, expires_at: datetime):
    db_token = models.RefreshToken(user_id=user_id, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.id == token).first()