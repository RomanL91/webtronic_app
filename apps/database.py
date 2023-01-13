import motor.motor_asyncio as moto

from bson.objectid import ObjectId
from pymongo import DESCENDING
from envparse import Env


# ================================================================================
# настройка БД
# ================================================================================
evn = Env()

MONGO_URL = evn.str('MONGO_URL', default='mongodb://localhost:27017/test_database')

client = moto.AsyncIOMotorClient(MONGO_URL)

database = client.webtronic_app

users_collection = database.users_collection
post_collection = database.post_collection

# добаляет в коллекцию индекс по полю email
users_collection.create_index(
    [('username', DESCENDING)],
    name='index_username',
    unique=True,
    background=True,
)


# ================================================================================
# # !!!!!!!! перевести на класс !!!!!!!!
# идея такая: создать менеджера коллекции, который выполняет стандартные
# CRUD операции с БД.
# # например:

# from typing import Union
# import asyncio

# class ManagerCollections():
#     def __init__(self, collection):
#         self.collection = collection

#     async def get_all_documents(self) -> list:
#         return [document for document in await self.collection.find().to_list(None)]

#     async def get_document(self, field: str, value: Union[str, int, ObjectId]):
#         return await self.collection.find_one({field: value})

#     async def delete_document(self, field: str, value: Union[str, int, ObjectId]):
#         await self.collection.delete_one({field: value})


# example = ManagerCollections(collection=users_collection)
# loop = asyncio.get_event_loop()
# documents = loop.create_task(example.get_all_documents())
# document = loop.create_task(example.get_document(
#     field='example=_id', value=ObjectId(oid='example=63bfa8e9eac126db7cb1fe84')))
# document_serch_username = loop.create_task(
#     example.get_document(field='example=username', value='example=Jon'))
# delete_document = loop.create_task(
#     example.delete_document(field='example=username', value='example=Jon'))
# loop.run_until_complete(asyncio.wait([documents, document, delete_document]))
# ================================================================================


# ================================================================================
# хелперы
def posr_helper(post) -> dict:
    return {
        'id': str(post['_id']),
        'title': str(post['title']),
        'content': str(post['content']),
        'count_like': int(post['count_like']),
        'count_dislike': int(post['count_dislike']),
        'created_at': str(post['created_at']),
        'author_mail': str(post['author_mail'])
    }


def user_helper(user) -> dict:
    return {
        'id': str(user['_id']),
        'username': str(user['username']),
        'email': str(user['email']),
    }


# ================================================================================
# функции БД для модели User
# ================================================================================

# забрать всех пользователей из БД
async def retrive_users():
    users = []
    async for user in users_collection.find():
        users.append(user_helper(user=user))
    return users


# добавить пользователя
async def add_user(user_data: dict) -> dict:
    user = await users_collection.insert_one(user_data)
    new_user = await users_collection.find_one({'_id': user.inserted_id})
    return user_helper(new_user)


# достать пользователя =)хахахах
async def retrive_user(id: str) -> dict:
    user = await users_collection.find_one({'_id': ObjectId(id)})
    if user:
        return user_helper(user=user)


# обновить пользователя
async def update_user(id: str, data: dict):
    print(data)
    if len(data) < 1:
        return False
    user = await users_collection.find_one({'_id': ObjectId(id)})
    print(user)
    if user:
        updata_user = await users_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': data}
        )
        if updata_user:
            return True
        return False


# удаление пользователя
async def del_user(id: str):
    user = await users_collection.find_one({'_id': ObjectId(id)})
    if user:
        await users_collection.delete_one({'_id': ObjectId(id)})
        return True


# получить пользователя по email
async def retrive_user_for_email(email: str) -> dict:
    user = await users_collection.find_one({'email': email})
    if user:
        return user


# получить пользователя по username
async def retrive_user_for_username(username: str) -> dict:
    user = await users_collection.find_one({'username': username})
    if user:
        return user


# ================================================================================
# функции БД для модели Post
# ================================================================================

# получить все посты ВСЕХ пользователей
async def retrive_posts_all_users():
    posts = []
    async for post in post_collection.find():
        posts.append(posr_helper(post=post))
    return posts


# добавить пост
async def add_post(post_data: dict) -> dict:
    post = await post_collection.insert_one(post_data)
    new_post = await post_collection.find_one({'_id': post.inserted_id})
    return posr_helper(new_post)


# редактировать пост
async def update_post(id: str, data: dict):
    if len(data) < 1:
        return False
    post = await post_collection.find_one({'_id': ObjectId(id)})
    if post:
        update_post = await post_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': data}
        )
        if update_post:
            return True
        return False


# удалить пост
async def del_post(id: str):
    post = await post_collection.find_one({'_id': ObjectId(id)})
    if post:
        await post_collection.delete_one({'_id': ObjectId(id)})
        return True


# достать пост(чтение 1 поста)
async def retrive_post(id: str) -> dict:
    post = await post_collection.find_one({'_id': ObjectId(id)})
    if post:
        return posr_helper(post)
