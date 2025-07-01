from fastapi import APIRouter

from app.api.users.v1.views import router as v1_router
user_routers = APIRouter()

user_routers.include_router(v1_router, prefix="/v1/users")