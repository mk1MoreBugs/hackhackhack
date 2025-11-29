from fastapi import APIRouter

from app.api.routes import users
from app.api.routes import auth
from app.api.routes import documents
from app.api.routes import chat


api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
