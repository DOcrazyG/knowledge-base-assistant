from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import user as user_models
from ...schemas import user as user_schemas
from ...utils.security import get_password_hash


async def create_user(db: AsyncSession, user: user_schemas.UserCreate):
    db_user = user_models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role_id=user.role_id,
    )
    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error creating user: {exc}")
        raise exc


async def get_user(db: AsyncSession, user_id: int):
    try:
        result = await db.execute(select(user_models.User).filter_by(id=user_id))
        return result.scalar_one_or_none()
    except Exception as exc:
        raise exc


async def get_users(db: AsyncSession):
    result = await db.execute(select(user_models.User))
    return result.scalars().all()


async def get_user_by_username(db: AsyncSession, username: str):
    try:
        result = await db.execute(select(user_models.User).filter_by(username=username))
        return result.scalar_one_or_none()
    except Exception as exc:
        raise exc


async def get_user_by_email(db: AsyncSession, email: str):
    try:
        result = await db.execute(select(user_models.User).filter_by(email=email))
        return result.scalar_one_or_none()
    except Exception as exc:
        raise exc


async def update_user(
    db: AsyncSession, user_id: int, user_update: user_schemas.UserUpdate
):
    db_user = await get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    update_data = user_update.model_dump(exclude_unset=True)
    try:
        for key, value in update_data.items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error updating user: {exc}")
        raise exc


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        await db.delete(db_user)
        await db.commit()
        return db_user
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error deleting user: {exc}")
        raise exc
