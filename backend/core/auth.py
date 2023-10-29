import time
from typing import Annotated, Union
from datetime import datetime, timedelta

from jose import jwt
from decouple import config
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from core.models.users import get_user_by_email
from core.schemas.users import UserSchema


SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')
# ACCESS_TOKEN_EXPIRE_MINUTES = float(config('ACCESS_TOKEN_EXPIRE_MINUTES'))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    cdata = data.copy()
    # cdata.update({'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    encoded_token = jwt.encode(cdata, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        print(e)
        return {}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = UserSchema(**get_user_by_email(username))
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user