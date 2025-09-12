from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..dependencies.depends import get_db
from ..dependencies.security import get_current_active_user, require_permission
from ..services.crud import role as role_crud
from ..schemas.role import Role, RoleCreate, RoleUpdate
from ..schemas.user import User

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=Role)
@require_permission("role:manage")
async def create_role(
    role: RoleCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await role_crud.create_role(db=db, role=role)


@router.get("/", response_model=List[Role])
async def read_roles(db: AsyncSession = Depends(get_db)):
    roles = await role_crud.get_roles(db)
    return roles


@router.get("/{role_id}", response_model=Role)
async def read_role(role_id: int, db: AsyncSession = Depends(get_db)):
    db_role = await role_crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role


@router.put("/{role_id}", response_model=Role)
@require_permission("role:manage")
async def update_role(
    role_id: int, 
    role: RoleUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_role = await role_crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return await role_crud.update_role(db=db, role_id=role_id, role_update=role)


@router.delete("/{role_id}")
@require_permission("role:manage")
async def delete_role(
    role_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_role = await role_crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return await role_crud.delete_role(db=db, role_id=role_id)