from sqlalchemy.orm import Session
from sqlalchemy import select, update
from fastapi import HTTPException, status
from loguru import logger

from ...schemas import role as role_schemas
from ...models import role as role_models


def create_role(db: Session, role: role_schemas.RoleCreate):
    db_role = role_models.Role(name=role.name)
    try:
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    except Exception as exc:
        logger.error(f"Error creating user: {exc}")
        raise exc


def get_role(db: Session, role_id: int):
    try:
        return db.execute(select(role_models.Role).filter_by(id=role_id)).scalar_one()
    except Exception:
        return None


def get_roles(db: Session):
    return db.execute(select(role_models.Role)).scalars().all()


def get_role_by_name(db: Session, role_name: str):
    try:
        return db.execute(select(role_models.Role).filter_by(name=role_name)).scalar_one()
    except Exception:
        return None

