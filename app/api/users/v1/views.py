from uuid import UUID
from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.user import UserResponseSchema, NewUserSchema
from app.models.user import UserModel
from app.core.database import get_db
from app.api.users.selectors import UserSelector

router = APIRouter()


@router.get("/", response_model=List[UserResponseSchema])
async def get_users(
        page: int = Query(0, ge=0, description="Number of users to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
        db: AsyncSession = Depends(get_db)
):
    """Get list of users with pagination"""
    users = await UserSelector.get_users(db, page=page, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(
        user_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """Get user by ID"""
    user = await UserSelector.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


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
