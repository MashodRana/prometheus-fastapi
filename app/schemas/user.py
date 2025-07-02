from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    is_active: bool = True


class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserInDB(UserBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    is_superuser: bool

    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
