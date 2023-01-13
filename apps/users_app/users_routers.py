from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import EmailStr

from .users_utils import (
    JWT_SECRET,
    verify_password, encrypt_password,
    encode_password, get_current_user
)


from apps.database import (
    retrive_users, retrive_user,
    retrive_user_for_username,
    add_user, update_user, del_user
)
from .users_model import (
    UserSchema,
    ResponseModel, ErrorResponseModel,
)


router = APIRouter()


# ================================================================================
# получить всех пользователей
@router.get('/all/', response_description='Users retrived.')
async def get_all_users():
    users = await retrive_users()
    if users:
        return ResponseModel(
            data=users,
            message='Users data retrived success.'
        )
    return ResponseModel(
        data=users,
        message='Empty list retutned.'
    )


# ================================================================================
# регистрация пользователя
@router.post('/register/', response_description='User data added into DB.')
async def user_registration(username: str = Form(), email: EmailStr = Form(), password: str = Form()):
    user_from_db = await retrive_user_for_username(username=username)
    password = await encrypt_password(password=password)
    if user_from_db is None:
        input_data = {'username': username,
                      'email': email, 'password': password}
        new_user = await add_user(user_data=input_data)
        return ResponseModel(
            data=new_user,
            message='User successfully registered.'
        )
    return ErrorResponseModel(
        error='An error occured.',
        code=404,
        message=f'User with username: {username} already exists.'
    )


# ================================================================================
# получить пользователя
@router.get('/{id}', response_description='User data retrived.')
async def get_user_data(id):
    try:
        user = await retrive_user(id)
    except:
        return ErrorResponseModel(
            error='An error occured.',
            code=404,
            message='User doesnt`t exist.'
        )
    if user:
        return ResponseModel(
            data=user,
            message='User data retrived success.'
        )


# ================================================================================
# редактировать пользователя
@router.put('/update/{id}', response_description='User update.')
async def update_user_data(id: str, username: str = Form(), password: str = Form()):
    req = {'username': username, 'password': password}
    try:
        updata_user = await update_user(id, req)
    except Exception as e:
        return ErrorResponseModel(
            error=f'User with username: {username} already exists.',
            code=404,
            message='Error updating user data.'
        )
    if updata_user:
        return ResponseModel(
            data='User with ID: {} updata success.'.format(id),
            message='User update success.'
        )
    return ErrorResponseModel(
        error='An error occured.',
        code=404,
        message='Error updating user data.'
    )


# ================================================================================
# удалить пользователя
@router.delete('/delete/{id}', response_description='User data delete from DB.')
async def del_user_data(id: str):
    delete_user = await del_user(id)
    if delete_user:
        return ResponseModel(
            data=f'User with ID: {id} removed.',
            message='User delete success.'
        )
    return ErrorResponseModel(
        error='An error occured.',
        code=404,
        message=f'User with ID {id} does not exist.'
    )


# ================================================================================
# получить токен
@router.post('/token')
async def generator_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await retrive_user_for_username(username=form_data.username)
    if not user:
        return ErrorResponseModel(
            error='An error occured.',
            code=400,
            message='This user does not exist.'
        )
    verif_passw = verify_password(
        input_password=form_data.password, hash_password_from_db=user['password'])
    if not verif_passw:
        return ErrorResponseModel(
            error='An error occured.',
            code=400,
            message=f'Wrong password for user: {user["username"]}.'
        )
    user.update({'_id': f'{user["_id"]}'})
    token = await encode_password(obj_user=dict(user), secret_str=JWT_SECRET)
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


# ================================================================================
# имитация получение своего профиля
@router.get('/profile/me')
async def get_user(current_user: UserSchema = Depends(get_current_user)):
    return current_user
