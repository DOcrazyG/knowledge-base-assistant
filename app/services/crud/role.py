from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update
from fastapi import HTTPException, status
from loguru import logger

from ...schemas import role as role_schemas
from ...models import role as role_models


async def create_role(db: AsyncSession, role: role_schemas.RoleCreate):
    db_role = role_models.Role(name=role.name)
    try:
        db.add(db_role)
        await db.commit()
        await db.refresh(db_role)
        return db_role
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error creating user: {exc}")
        raise exc


async def get_role(db: AsyncSession, role_id: int):
    try:
        result = await db.execute(
            select(role_models.Role)
            .options(selectinload(role_models.Role.permissions))
            .filter_by(id=role_id)
        )
        return result.scalar_one_or_none()
    except Exception as exc:
        raise exc


async def get_role_by_name(db: AsyncSession, name: str):
    try:
        result = await db.execute(
            select(role_models.Role)
            .options(selectinload(role_models.Role.permissions))
            .filter_by(name=name)
        )
        return result.scalar_one_or_none()
    except Exception as exc:
        raise exc


async def get_roles(db: AsyncSession):
    result = await db.execute(
        select(role_models.Role).options(selectinload(role_models.Role.permissions))
    )
    return result.scalars().all()


async def update_role(
    db: AsyncSession, role_id: int, role_update: role_schemas.RoleUpdate
):
    db_role = await get_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    try:
        db_role.name = role_update.name
        await db.commit()
        await db.refresh(db_role)
        return db_role
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error updating role: {exc}")
        raise HTTPException(status_code=400, detail="Error updating role") from exc


async def delete_role(db: AsyncSession, role_id: int):
    db_role = await get_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    try:
        await db.delete(db_role)
        await db.commit()
        return {"message": "Role deleted successfully"}
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error deleting role: {exc}")
        raise HTTPException(status_code=400, detail="Error deleting role") from exc
