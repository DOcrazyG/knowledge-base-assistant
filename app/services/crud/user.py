from sqlalchemy.orm import Session
from sqlalchemy import select, update
from fastapi import HTTPException, status
from loguru import logger

from ...schemas import user as user_schemas
from ...models import user as user_models
from ...dependencies.security import get_password_hash


def create_user(db: Session, user: user_schemas.UserCreate):
    db_user = user_models.User(
        username=user.username, email=user.email, hashed_password=get_password_hash(user.password), role_id=user.role_id
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as exc:
        logger.error(f"Error creating user: {exc}")
        raise exc


def get_user(db: Session, user_id: int):
    return db.get(user_id)


def get_users(db: Session):
    return db.execute(select(user_models.User)).scalars().all()


def get_user_by_username(db: Session, username: str):
    try:
        return db.execute(select(user_models.User).filter_by(username=username)).scalar_one()
    except Exception:
        return None


def get_user_by_email(db: Session, email: str):
    try:
        return db.execute(select(user_models.User).filter_by(email=email)).scalar_one()
    except Exception:
        return None


def update_user(db: Session, user_id: int, user_update: user_schemas.UserBase):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    try:
        # db.execute(update(db_user), update_data)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as exc:
        logger.error(f"Error updating user: {exc}")
        raise exc


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        db.delete(db_user)
        db.commit()
        return db_user
    except Exception as exc:
        logger.error(f"Error deleting user: {exc}")
        raise exc
