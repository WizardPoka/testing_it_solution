# app/crud.py

from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Adverts CRUD ---

def get_advert(db: Session, advert_id: int):
    return db.query(models.Advert).filter(models.Advert.id == advert_id).first()

def get_adverts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Advert).offset(skip).limit(limit).all()

def create_advert(db: Session, advert: schemas.AdvertCreate):
    db_advert = models.Advert(**advert.dict())
    db.add(db_advert)
    db.commit()
    db.refresh(db_advert)
    return db_advert

def delete_advert(db: Session, advert_id: int):
    db_advert = db.query(models.Advert).filter(models.Advert.id == advert_id).first()
    db.delete(db_advert)
    db.commit()
    return db_advert

def update_advert(db: Session, advert_id: int, advert: schemas.AdvertCreate):
    db_advert = db.query(models.Advert).filter(models.Advert.id == advert_id).first()
    for key, value in advert.dict().items():
        setattr(db_advert, key, value)
    db.commit()
    db.refresh(db_advert)
    return db_advert

# --- User CRUD ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
