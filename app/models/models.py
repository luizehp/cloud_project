from sqlmodel import SQLModel, Field
from datetime import date, time
from typing import Optional, Union


class UserModel(SQLModel):
    nome: str = Field(nullable=False, index=True)
    email: str = Field(nullable=False, index=True)
    senha: str = Field(nullable=False)

class User(UserModel, table=True):
    id: int | None = Field(default=None, primary_key=True, nullable=False)

class UserCreate(UserModel):
    pass

class UserLogin(SQLModel):
    email: str
    senha: str 


class UserUpdate(SQLModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[int] = None
