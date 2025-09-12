from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..dependencies.depends import get_db
from ..dependencies.security import get_current_active_user, require_permission
from ..services.crud import user as user_crud
from ..schemas.user import User, UserCreate, UserUpdate
from ..schemas.role import Role

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=User)
@require_permission("user:manage")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_user = await user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await user_crud.create_user(db=db, user=user)


@router.get("/", response_model=List[User])
@require_permission("user:manage")
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    users = await user_crud.get_users(db)
    return users


@router.get("/me", response_model=User)
async def read_users_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.get("/{user_id}", response_model=User)
@require_permission("user:manage")
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_user = await user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=User)
@require_permission("user:manage")
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_user = await user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_crud.update_user(db=db, user_id=user_id, user_update=user)


@router.delete("/{user_id}")
@require_permission("user:manage")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_user = await user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await user_crud.delete_user(db=db, user_id=user_id)
    return {"message": "User deleted successfully"}
