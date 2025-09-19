from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from loguru import logger

from ...schemas import file as file_schemas
from ...models import file as file_models


async def create_file(db: AsyncSession, file_data: file_schemas.FileCreate):
    """
    创建文件记录
    """
    db_file = file_models.File(
        user_id=file_data.user_id,
        minio_path=file_data.minio_path,
        filename=file_data.filename,
        size=file_data.size,
    )
    try:
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)
        return db_file
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error creating file: {exc}")
        raise exc


async def get_file(db: AsyncSession, file_id: int):
    """
    获取文件信息
    """
    try:
        result = await db.execute(
            select(file_models.File).where(file_models.File.id == file_id)
        )
        return result.scalar_one_or_none()
    except Exception as exc:
        logger.error(f"Can not find file: {exc}")
        raise exc


async def get_files(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    """
    获取用户文件列表
    """
    try:
        result = await db.execute(
            select(file_models.File)
            .where(file_models.File.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except Exception as exc:
        logger.error(f"Error getting files: {exc}")
        raise exc


async def delete_file(db: AsyncSession, file_id: int):
    """
    删除文件记录
    """
    result = await db.execute(
        select(file_models.File).where(file_models.File.id == file_id)
    )
    db_file = result.scalar_one_or_none()

    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件未找到")
    try:
        await db.delete(db_file)
        await db.commit()
        return db_file
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error deleting file: {exc}")
        raise exc
