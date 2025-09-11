from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..core.database import SessionLocal
from ..schemas.user import UserCreate, User, UserUpdate
from ..services.crud import user as user_crud
from ..dependencies.depends import get_db
from ..dependencies.security import get_current_active_user

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=list[User])
async def get_users(db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    return user_crud.get_users(db)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    db_user = user_crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.post("/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    if user_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    return user_crud.create_user(db, user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)
):
    db_user = user_crud.update_user(db, user_id, user)
    return db_user


@router.delete("/{user_id}", response_model=User)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)):
    db_user = user_crud.delete_user(db, user_id)
    return db_user
