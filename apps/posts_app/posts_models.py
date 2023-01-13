from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class PostSchema(BaseModel):
    title: str = Field(..., max_length=100)
    content: str = Field(...)
    count_like: int = Field(default=0)
    count_dislike: int = Field(default=0)
    created_at: datetime = Field(default=datetime.now())
    author_mail: EmailStr = Field(...)

    class Config:
        schema_extra = {
            'example': {
                'title': 'title',
                'content': 'content',
                'count_like': 0,
                'count_dislike': 0,
                'created_at': datetime.now(),
                'author_mail': 'author_mail@mail.ru'
            }
        }


class UpdatePost(BaseModel):
    title: Optional[str]
    content: Optional[str]

    class Config:
        schema_extra = {
            'example': {
                'title': 'title',
                'content': 'content',
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
