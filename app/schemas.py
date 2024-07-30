# app/schemas.py

from pydantic import BaseModel
from typing import Optional

class AdvertBase(BaseModel):
    title: str
    author: str
    views: int
    position: int

class AdvertCreate(AdvertBase):
    pass

class Advert(AdvertBase):
    id: int

    class Config:
        from_attributes = True  # Обновлено для Pydantic V2

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # Обновлено для Pydantic V2

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
