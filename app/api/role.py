from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..core.database import SessionLocal
from ..schemas.role import RoleCreate, Role, RoleUpdate
from ..services.crud import role as role_crud
from ..dependencies.depends import get_db
from ..dependencies.security import get_current_active_user

router = APIRouter(prefix="/role", tags=["role"])


@router.get("/", response_model=list[Role])
async def get_roles(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return role_crud.get_roles(db)


@router.get("/{role_id}", response_model=Role)
async def get_role(role_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    db_role = role_crud.get_role(db, role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return db_role


@router.post("/create", response_model=Role)
async def create_role(role: RoleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    if role_crud.get_role_by_name(db, role.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rolename already exists")

    return role_crud.create_role(db, role)


@router.delete("/delete/{role_id}", response_model=Role)
async def delete_role(role_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    db_role = role_crud.get_role(db, role_id)
    if db_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role_crud.delete_role(db, role_id)
