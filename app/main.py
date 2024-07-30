# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app import models, schemas, crud, auth, database, scraper

# Создание базы данных
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Эндпоинты для работы с объявлениями ---

@app.post("/adverts/", response_model=schemas.Advert)
def create_advert(
    advert: schemas.AdvertCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Создать новое объявление
    """
    return crud.create_advert(db=db, advert=advert)

@app.get("/adverts/", response_model=List[schemas.Advert])
def read_adverts(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Получить список объявлений
    """
    adverts = crud.get_adverts(db, skip=skip, limit=limit)
    return adverts

@app.get("/adverts/{advert_id}", response_model=schemas.Advert)
def read_advert(
    advert_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Получить объявление по ID
    """
    db_advert = crud.get_advert(db, advert_id=advert_id)
    if db_advert is None:
        raise HTTPException(status_code=404, detail="Advert not found")
    return db_advert

@app.delete("/adverts/{advert_id}", response_model=schemas.Advert)
def delete_advert(
    advert_id: int, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Удалить объявление
    """
    db_advert = crud.get_advert(db, advert_id=advert_id)
    if db_advert is None:
        raise HTTPException(status_code=404, detail="Advert not found")
    return crud.delete_advert(db=db, advert_id=advert_id)

@app.put("/adverts/{advert_id}", response_model=schemas.Advert)
def update_advert(
    advert_id: int, 
    advert: schemas.AdvertCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Обновить объявление
    """
    db_advert = crud.get_advert(db, advert_id=advert_id)
    if db_advert is None:
        raise HTTPException(status_code=404, detail="Advert not found")
    return crud.update_advert(db=db, advert=advert, advert_id=advert_id)

# --- Эндпоинты для работы с пользователями ---

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# --- Новый эндпоинт для парсинга и сохранения объявлений ---

@app.post("/parse-adverts/")
def parse_and_save_adverts(
    db: Session = Depends(get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """
    Парсинг первых 10 объявлений с FarPost и сохранение их в базу данных
    """
    adverts = scraper.parse_adverts()
    crud.save_adverts(db, adverts)
    return {"message": "Adverts parsed and saved successfully"}
