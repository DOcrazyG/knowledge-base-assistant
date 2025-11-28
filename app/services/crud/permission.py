from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import permission as permission_models
from ...models import role as role_models
from ...models.permission import RolePermission
from ...schemas import permission as permission_schemas


async def create_permission(
    db: AsyncSession, permission: permission_schemas.PermissionCreate
):
    db_permission = permission_models.Permission(
        name=permission.name, description=permission.description
    )
    try:
        db.add(db_permission)
        await db.commit()
        await db.refresh(db_permission)
        return db_permission
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error creating permission: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Permission already exists"
        ) from exc


async def get_permission(db: AsyncSession, permission_id: int):
    try:
        result = await db.execute(
            select(permission_models.Permission).filter_by(id=permission_id)
        )
        return result.scalar_one_or_none()
    except Exception as exc:
        logger.error(f"Error getting permission: {exc}")
        return None


async def get_permission_by_name(db: AsyncSession, name: str):
    try:
        result = await db.execute(
            select(permission_models.Permission).filter_by(name=name)
        )
        return result.scalar_one_or_none()
    except Exception as exc:
        logger.error(f"Error getting permission by name: {exc}")
        return None


async def get_permissions(db: AsyncSession):
    try:
        result = await db.execute(select(permission_models.Permission))
        return result.scalars().all()
    except Exception as exc:
        logger.error(f"Error getting permissions: {exc}")
        return []


async def update_permission(
    db: AsyncSession,
    permission_id: int,
    permission_update: permission_schemas.PermissionUpdate,
):
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )

    try:
        db_permission.name = permission_update.name
        db_permission.description = permission_update.description
        await db.commit()
        await db.refresh(db_permission)
        return db_permission
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error updating permission: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating permission"
        ) from exc


async def delete_permission(db: AsyncSession, permission_id: int):
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )

    try:
        await db.delete(db_permission)
        await db.commit()
        return {"message": "Permission deleted successfully"}
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error deleting permission: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting permission"
        ) from exc


async def assign_permission_to_role(db: AsyncSession, role_id: int, permission_id: int):
    # Check if role exists
    result = await db.execute(select(role_models.Role).filter_by(id=role_id))
    db_role = result.scalar_one_or_none()
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    # Check if permission exists
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )

    # Check if the relationship already exists
    result = await db.execute(
        select(RolePermission).filter_by(role_id=role_id, permission_id=permission_id)
    )
    existing_relationship = result.scalar_one_or_none()

    if existing_relationship:
        logger.info(f"Permission {permission_id} already assigned to role {role_id}")
        return {"message": "Permission already assigned to role"}

    try:
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        db.add(role_permission)
        await db.commit()
        await db.refresh(role_permission)
        return {"message": "Permission assigned to role successfully"}
    except Exception as exc:
        await db.rollback()
        logger.error(
            f"Error assigning permission {permission_id} to role {role_id}: {exc}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error assigning permission to role: {exc}",
        ) from exc


async def remove_permission_from_role(
    db: AsyncSession, role_id: int, permission_id: int
):
    # Check if role exists
    result = await db.execute(select(role_models.Role).filter_by(id=role_id))
    db_role = result.scalar_one_or_none()
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    # Check if permission exists
    db_permission = await get_permission(db, permission_id)
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )

    # Check if the relationship exists
    result = await db.execute(
        select(RolePermission).filter_by(role_id=role_id, permission_id=permission_id)
    )
    role_permission = result.scalar_one_or_none()

    if not role_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission not assigned to role",
        )

    try:
        await db.delete(role_permission)
        await db.commit()
        return {"message": "Permission removed from role successfully"}
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error removing permission from role: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error removing permission from role",
        ) from exc
