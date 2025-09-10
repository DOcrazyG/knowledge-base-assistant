from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..core.database import SessionLocal
from ..schemas.role import RoleCreate, Role
from ..services.crud import role as role_crud

router = APIRouter(prefix="/role", tags=["role"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[Role])
def get_roles(db: Session = Depends(get_db)):
    return role_crud.get_roles(db)


@router.post("/create", response_model=Role)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    if role_crud.get_role_by_name(db, role.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rolename already exists")

    return role_crud.create_role(db, role)
