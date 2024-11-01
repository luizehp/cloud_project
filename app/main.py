from sqlalchemy.engine import Connection
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import sqlalchemy
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import Depends, FastAPI, HTTPException, Query
import json
import os
from typing import List, Union
from models import *
from typing import Annotated
from jose import JWTError, jwt
from datetime import datetime, timedelta
import bcrypt
import requests
from bs4 import BeautifulSoup

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


load_dotenv()
app = FastAPI()

user = os.getenv("USER")
secret_key = os.getenv("PASSWORD")
server = os.getenv("SERVER")
port = os.getenv("PORT")
database_name = os.getenv("NAME")


def getdados():

    url = "https://datadehoje.com/"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data_hoje = str(soup.find('p', {'id': 'fecha'})) .split("span")[1][2:-2]

    return data_hoje


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Step 2: Verify the password during login


def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

# Create a payload for the JWT


def create_jwt(email):
    expire = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    payload = {
        "sub": email,
        "exp": expire,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None


mysql_url = f"mysql+mysqlconnector://{user}:{secret_key}@{server}:{port}"

mysql_url_db = f"mysql+mysqlconnector://{user}:{secret_key}@{server}:{port}/{database_name}"


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_database(engine: Connection, database_name: str):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database_name}"))
        conn.execute(text(f"USE {database_name}"))
        conn.commit()


engine = create_engine(mysql_url, echo=True)
enginedb = create_engine(mysql_url_db, echo=True)


@app.on_event("startup")
def on_startup(engine=engine, enginedb=enginedb):
    create_database(engine, database_name)
    SQLModel.metadata.create_all(enginedb)


# CRUD for Users


@app.post("/resgistrar/", tags=["User"], summary='Creates a new user')
def create_user(user: UserCreate, session: SessionDep):

    check = session.exec(select(User).where(User.email == user.email)).first()
    if check:
        raise HTTPException(status_code=409, detail="email já registrado")

    user = User.from_orm(user)
    user.senha = hash_password(user.senha)
    session.add(user)
    session.commit()
    session.refresh(user)

    jwt = create_jwt(user.email)
    print("JWT:", jwt)
    return {"jwt": jwt}


@app.post("/login/", tags=["User"], summary='login')
def login(user: UserLogin, session: SessionDep):

    db_user = session.exec(select(User).where(
        User.email == user.email)).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="email não encontrado")

    if not bcrypt.checkpw(user.senha.encode('utf-8'), db_user.senha.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    jwt_token = create_jwt(db_user.email)

    return {"jwt": jwt_token}


@app.get("/consultar/", tags=["User"], summary='Fetches all users')
def read_users(JWTToken: str):
    payload = verify_jwt(JWTToken)
    if payload is None:
        raise HTTPException(status_code=403, detail="JWT ausente ou inválido")
    print("PAYLOAD", payload)
    return getdados()
