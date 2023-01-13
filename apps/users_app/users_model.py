from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'username': 'RomanL91',
                'email': 'roman@mail.com',
                'password': 'passwd'
            }
        }


class UpdateUser(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]

    class Config:
        schema_extra = {
            'example': {
                'username': 'RomanL1991',
                'email': 'roman1991@mail.com',
                'password': 'passwd'
            }
        }


def ResponseModel(data, message):
    return {
        'data': [data],
        'code': 200,
        'message': message,
    }


def ErrorResponseModel(error, code, message):
    return {
        'error': error,
        'code': code,
        'message': message,
    }
