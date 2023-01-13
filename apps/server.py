from fastapi import FastAPI

from apps.users_app.users_routers import router as UserRouter
from apps.posts_app.posts_routers import router as PostRouter


server = FastAPI()

server.include_router(UserRouter, tags=['User'], prefix='/user')
server.include_router(PostRouter, tags=['Post'], prefix='/post')
