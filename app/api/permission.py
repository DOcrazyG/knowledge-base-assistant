from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies.depends import get_db
from ..dependencies.security import get_current_active_user, require_permission
from ..schemas.permission import Permission, PermissionCreate, PermissionUpdate
from ..schemas.user import User
from ..services.crud import permission as permission_crud

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.post("/", response_model=Permission)
@require_permission("permission:manage")
async def create_permission(
    permission: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_permission = await permission_crud.get_permission_by_name(
        db, name=permission.name
    )
    if db_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Permission already exists"
        )
    return await permission_crud.create_permission(db=db, permission=permission)


@router.get("/", response_model=List[Permission])
@require_permission("permission:manage")
async def read_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    permissions = await permission_crud.get_permissions(db)
    return permissions


@router.get("/{permission_id}", response_model=Permission)
@require_permission("permission:manage")
async def read_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_permission = await permission_crud.get_permission(
        db, permission_id=permission_id
    )
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return db_permission


@router.put("/{permission_id}", response_model=Permission)
@require_permission("permission:manage")
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_permission = await permission_crud.get_permission(
        db, permission_id=permission_id
    )
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return await permission_crud.update_permission(
        db=db, permission_id=permission_id, permission_update=permission_update
    )


@router.delete("/{permission_id}")
@require_permission("permission:manage")
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_permission = await permission_crud.get_permission(
        db, permission_id=permission_id
    )
    if not db_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return await permission_crud.delete_permission(db=db, permission_id=permission_id)


@router.post("/{role_id}/permissions/{permission_id}")
@require_permission("permission:manage")
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await permission_crud.assign_permission_to_role(
        db=db, role_id=role_id, permission_id=permission_id
    )


@router.delete("/{role_id}/permissions/{permission_id}")
@require_permission("permission:manage")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await permission_crud.remove_permission_from_role(
        db=db, role_id=role_id, permission_id=permission_id
    )
