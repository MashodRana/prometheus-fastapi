from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.user import UserResponseSchema, UserCreateSchema, NewUserSchema
from app.models.user import UserModel
from app.core.database import get_db
from app.api.users.selectors import UserSelector

router = APIRouter()


@router.get("/")
async def get_users():
    return JSONResponse({"message": "from all users."})


@router.post("/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
        new_user: NewUserSchema,
        db: AsyncSession = Depends(get_db)
):
    """Create new user"""
    try:
        user = await UserSelector.create(db=db, new_user=new_user)

        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
