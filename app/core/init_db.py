import asyncio
from .database import Base, engine
from loguru import logger
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import SessionLocal
from ..models.user import User
from ..models.role import Role
from ..models.knowledge_item import KnowledgeItem
from ..models.file import File
from ..models.chat_history import ChatHistory
from ..models.permission import Permission, RolePermission

from ..schemas.role import RoleCreate
from ..schemas.user import UserCreate
from ..schemas.permission import PermissionCreate
from ..services.crud.role import get_role_by_name, create_role
from ..services.crud.user import get_user_by_username, get_user_by_email, create_user
from ..services.crud.permission import (
    get_permission_by_name,
    create_permission,
    assign_permission_to_role,
)


async def create_tables():
    # create all tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")


async def init_data():
    # Create a new async session using SessionLocal
    async_session = SessionLocal()
    
    try:
        # Create default permissions
        permissions = [
            {"name": "role:manage", "description": "Manage roles"},
            {"name": "user:manage", "description": "Manage users"},
            {"name": "permission:manage", "description": "Manage permissions"},
            {"name": "role:view", "description": "View roles"},
            {"name": "user:view", "description": "View users"},
        ]

        for perm_data in permissions:
            perm = await get_permission_by_name(async_session, perm_data["name"])
            if not perm:
                perm_create = PermissionCreate(
                    name=perm_data["name"], description=perm_data["description"]
                )
                perm = await create_permission(async_session, perm_create)
                logger.info(f"Permission created: {perm.name}")

        # Create user role
        user_role = await get_role_by_name(async_session, "user")
        if not user_role:
            user_role = RoleCreate(name="user")
            user_role = await create_role(async_session, user_role)
            logger.info(f"Role 'user' created: {user_role}")
        
        # Assign permissions to user role
        user_permission = permissions[3:]  # role:view and user:view
        for perm in user_permission:
            perm = await get_permission_by_name(async_session, perm["name"])
            if perm:
                await assign_permission_to_role(async_session, user_role.id, perm.id)
                logger.info(f"Assigned permission {perm.name} to user role")

        # Create admin role
        admin_role = await get_role_by_name(async_session, "admin")
        if not admin_role:
            admin_role = RoleCreate(name="admin")
            admin_role = await create_role(async_session, admin_role)
            logger.info(f"Role 'admin' created: {admin_role}")

        # Assign all permissions to admin role
        result = await async_session.execute(select(Permission))
        all_permissions = result.scalars().all()
        logger.info(f"Found {len(all_permissions)} permissions to assign to admin role")
        
        for perm in all_permissions:
            try:
                await assign_permission_to_role(async_session, admin_role.id, perm.id)
                logger.info(f"Assigned permission {perm.name} to admin role")
            except Exception as e:
                logger.error(
                    f"Could not assign permission {perm.name} (ID: {perm.id}) to admin role (ID: {admin_role.id}): {e}"
                )

        # Create admin user if it doesn't exist
        try:
            admin_exists = await get_user_by_username(async_session, "admin") or \
                          await get_user_by_email(async_session, "admin@example.com")
            
            if admin_exists:
                logger.debug("Admin user already exists")
            else:
                admin_user = UserCreate(
                    username="admin",
                    email="admin@example.com",
                    password="123456",
                    role_id=admin_role.id,
                )
                admin_user = await create_user(async_session, admin_user)
                logger.info(f"Admin user created: {admin_user}")
        except Exception as exc:
            logger.error(f"Error inserting admin user: {exc}")
            raise exc
            
        # Commit the transaction
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        logger.error(f"Error during data initialization: {e}")
        raise e
    finally:
        # Ensure the session is properly closed
        await async_session.close()


async def init_all():
    await create_tables()
    await init_data()


if __name__ == "__main__":
    asyncio.run(init_all())