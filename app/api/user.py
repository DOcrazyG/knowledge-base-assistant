from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..core.database import SessionLocal
from ..schemas.user import UserCreate, User
from ..services.crud import user as user_crud

router = APIRouter(prefix="/user", tags=["user"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    return user_crud.get_users(db)


@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    if user_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    return user_crud.create_user(db, user)
