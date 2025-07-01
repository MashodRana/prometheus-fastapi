from fastapi import APIRouter

from app.api.users.routers import user_routers

api_router = APIRouter()

api_router.include_router(user_routers)
