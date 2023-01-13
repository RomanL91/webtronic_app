from typing import Union
from fastapi import APIRouter, Depends, Form

from apps.database import (
    retrive_posts_all_users, retrive_post,
    add_post, update_post, del_post
)

from .posts_models import (
    PostSchema,
    ResponseModel, ErrorResponseModel
)

from ..users_app.users_model import UserSchema
from ..users_app.users_utils import get_current_user


router = APIRouter()


# # ================================================================================
# все посты всех пользователей
@router.get('/all/', response_description='Get all posts from all users.')
async def get_all_posts(current_user: UserSchema = Depends(get_current_user)):
    posts = await retrive_posts_all_users()
    if posts:
        return ResponseModel(
            data=posts,
            message='Posts data retrived success.'
        )
    return ResponseModel(
        data=posts,
        message='Empty list retutned.'
    )


# ================================================================================
# добавить пост
@router.post('/create/', response_description='Post data added into DB.')
async def add_post_data(title: str = Form(), content: str = Form(),
                        current_user: UserSchema = Depends(get_current_user)):
    if current_user:
        input_data = {'title': title, 'content': content,
                      'author_mail': current_user['email']}
        post_models = PostSchema.__fields__
        post = post_models.copy()
        data = {}
        for k, v in post.items():
            if k in input_data:
                post.update(input_data)
            else:
                data.setdefault(k, v.get_default())
        post.update(data)
        new_post = await add_post(post_data=post)
        # del post
        return ResponseModel(
            data=new_post,
            message='Post data added successfully.'
        )
    return ErrorResponseModel(
        error='An error occured.',
        code=404,
        message='There is no user with {} mail.'.format(current_user.email)
    )


# ================================================================================
# получить пост
@router.get('/{id}', response_description='Post data retrived.')
async def get_post_data(id: str, current_user: UserSchema = Depends(get_current_user)):
    post = await retrive_post(id)
    if post:
        return ResponseModel(
            data=post,
            message='Post data retrived success.'
        )
    return ErrorResponseModel(
        error='An error occured.',
        code=404,
        message='Post doesnt`t exist.'
    )


# ================================================================================
# редактировать пост
@router.put('/{id}', response_description='Post update.')
async def update_post_data(id: str, title: str = Form(), content: str = Form(),
                           current_user: UserSchema = Depends(get_current_user)):
    input_data = {'title': title, 'content': content}
    post_from_db = await update_post(id, input_data)
    if post_from_db:
        return ResponseModel(
            data='Post with ID: {} updata success.'.format(id),
            message='Post update success.'
        )
    return ErrorResponseModel(
        error='An error occured.',
        code=404,
        message='Error updating user data.'
    )


# ================================================================================
# удалить пост
@router.delete('/{id}', response_description='Post data delete from DB.')
async def delete_post_data(id: str, current_user: UserSchema = Depends(get_current_user)):
    delete_post = await del_post(id)
    if delete_post:
        return ResponseModel(
            data='Post with ID: {} removed.'.format(id),
            message='Post delete success.'
        )
    return ErrorResponseModel(
        error='An error occured.',
        code=404,
        message='Post with ID {0} doesn`t exist.'.format(id)
    )


# ================================================================================
# like
@router.post('/{id}', response_description='Post got a like/dislike.')
async def likes_dislikes(id: str, like: Union[bool, None] = None, dislike: Union[bool, None] = None,
                         current_user: UserSchema = Depends(get_current_user)):
    input_data = {
        'user_rater': current_user['username'], 'like': like, 'dislike': dislike}
    post = await retrive_post(id)
    if current_user['email'] == post['author_mail']:
        return ErrorResponseModel(
            error='error',
            code=404,
            message=' '.join(
                (
                    f'You: {current_user["username"]} are the author of the post: {post["title"]}.',
                    f'Evaluation for you is not available.'
                )
            )
        )
    # тут интересный момент, возможны разные вариации
    # предположим, что у нас кнопки по типу как на youtube
    # нажатие на которую отсылает POST запрос, так как нельзя нажать
    # 2 кнопки одновременно логика блока IF простая.
    # Дополнительно: мы не храним состояние о том, что мы лайкнули/дизлайкнули,
    # что освобождает от логики "снятия лайка/дизлайка"
    if input_data['like'] == input_data['dislike']:
        return ErrorResponseModel(
            error=f'error...',
            code=404,
            message=f'You cannot press 2 buttons(like|dislike) at the same time.'
        )
    if input_data['like']:
        post['count_like'] += 1
        post_from_db = await update_post(id=id, data=post)
        return ResponseModel(
            data=f'Number of likes: {post["count_like"]}.',
            message=f'You: {current_user["username"]} liked the post: {post["title"]}!'
        )
    elif input_data['dislike']:
        post['count_dislike'] += 1
        post_from_db = await update_post(id=id, data=post)
        return ResponseModel(
            data=f'Number of dislike: {post["count_dislike"]}.',
            message=f'You: {current_user["username"]} dislike the post: {post["title"]}!'
        )
    else:
        return ErrorResponseModel(
            error=f'Value is invalid.',
            code=400,
            message=f'Will not work, {current_user["username"]}!'
        )
