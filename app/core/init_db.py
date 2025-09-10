from .database import Base, engine, SessionLocal
from loguru import logger
from sqlalchemy import text

from ..models.user import User
from ..models.role import Role
from ..models.knowledge_item import KnowledgeItem
from ..models.file import File
from ..models.chat_history import ChatHistory

from ..schemas.role import RoleCreate
from ..schemas.user import UserCreate
from ..services.crud.role import get_role_by_name, create_role
from ..services.crud.user import get_user_by_username, get_user_by_email, create_user


def create_tables():
    # create all tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.success("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")


def init_data():
    db = SessionLocal()
    # create role of user
    user_role = get_role_by_name(db, "user")
    if not user_role:
        user_role = RoleCreate(name="user")
        user_role = create_role(db, user_role)
        logger.info(f"Role of user created: {user_role}")

    # create role of admin
    admin_role = get_role_by_name(db, "admin")
    if not admin_role:
        admin_role = RoleCreate(name="admin")
        admin_role = create_role(db, admin_role)
        logger.info(f"Role of admin created: {admin_role}")

    # create user of admin
    try:
        if get_user_by_username(db, "admin") or get_user_by_email(db, "admin@example.com"):
            logger.debug("Admin user already exists")
        else:
            admin_user = UserCreate(
                username="admin",
                email="admin@example.com",
                password="123456",
                role_id=admin_role.id,
            )
            admin_user = create_user(db, admin_user)
            logger.info(f"Admin user created: {admin_user}")
    except Exception as exc:
        logger.error(f"Error inserting admin user: {exc}")
        raise exc


if __name__ == "__main__":
    create_tables()
    init_data()
