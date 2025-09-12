import jwt

from passlib.context import CryptContext
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from jwt.exceptions import InvalidTokenError
from functools import wraps

from ..services.crud import user as user_crud
from ..services.crud import role as role_crud
from ..schemas.user import User
from .depends import get_db

SECRET_KEY = "529714b91fa8d47963bb5cd4770d1347ca338a1d454f5c5831c619bd36b73ee4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


from ..utils.security import verify_password, get_password_hash


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await user_crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: Annotated[AsyncSession, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await user_crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_permissions(db: AsyncSession, user_id: int) -> List[str]:
    """
    Get all permissions for a user based on their role
    """
    user = await user_crud.get_user(db, user_id)
    if not user:
        return []
        
    role = await role_crud.get_role(db, user.role_id)
    if not role:
        return []
        
    return [permission.name for permission in role.permissions]


async def check_user_permission(db: AsyncSession, user_id: int, required_permission: str) -> bool:
    """
    Check if a user has a specific permission
    """
    user_permissions = await get_current_user_permissions(db, user_id)
    return required_permission in user_permissions


def require_permission(permission: str):
    """
    Decorator to require a specific permission for an endpoint
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the database and current user from the function arguments
            db = kwargs.get('db')
            current_user = kwargs.get('current_user')
            
            if not db or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Database or user not provided"
                )
            
            if not await check_user_permission(db, current_user.id, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            # Call the original function
            result = await func(*args, **kwargs)
            return result
        return wrapper
    return decorator