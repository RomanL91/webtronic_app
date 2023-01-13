from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import jwt

from envparse import Env

from passlib.hash import bcrypt as crypt

from ..database import retrive_user, retrive_user_for_username


# конечная точка на которой будет генерироваться токек
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/token')

evn = Env()

JWT_SECRET = evn.str('JWT_SECRET')
ALGORITM = evn.str('ALGORITM')


# ================================================================================
# utils for user_app
# ================================================================================

async def encode_password(obj_user: dict, secret_str: str) -> str:
    return jwt.encode(payload=obj_user, key=secret_str)


async def encrypt_password(password):
    return crypt.hash(password)


def verify_password(input_password, hash_password_from_db):
    return crypt.verify(secret=input_password, hash=hash_password_from_db)


async def get_auten_user(username: str, password: str):
    user = await retrive_user_for_username(username=username)
    if not user:
        return False
    if not verify_password(input_password=password, hash_password_from_db=user['password']):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(jwt=token, key=JWT_SECRET, algorithms=ALGORITM)
        user_id = payload.get('_id')
        user = await retrive_user(id=user_id)
        print(user)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid credential')
    return user
