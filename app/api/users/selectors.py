from uuid import UUID
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.user import UserModel
from app.schemas.user import NewUserSchema


class UserSelector:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> Optional[UserModel]:
        result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(db: AsyncSession, page: int = 0, limit: int = 100) -> List[UserModel]:
        skip = page * limit
        result = await db.execute(
            select(UserModel)
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, new_user: NewUserSchema) -> UserModel:
        try:
            user = UserModel(
                email=new_user.email,
                username=new_user.username,
                full_name=new_user.full_name,
                bio=new_user.bio,
                hashed_password=new_user.password,
                is_active=new_user.is_active,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except IntegrityError:
            await db.rollback()
            raise ValueError("Email or username already exists")
