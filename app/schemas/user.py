from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    # is_active: Optional[bool] = True
    role_id: Optional[int] = 1


class User(UserBase):
    id: int
    # is_active: bool
    # role_id: int
    # create_at: datetime
    # update_at: datetime

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    is_active: Optional[bool] = True
    role_id: Optional[int] = 1


class UserDelete(UserBase):
    pass


class UserLogin(UserBase):
    password: str
