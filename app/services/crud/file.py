from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models import file as file_models
from ...schemas import file as file_schemas


async def create_file(db: AsyncSession, create_data: file_schemas.FileCreate):
    """
    创建文件记录
    """
    # 根据user_id和filename查找文件是否存在
    result = await db.execute(
        select(file_models.File)
        .where(file_models.File.user_id == create_data.user_id)
        .where(file_models.File.filename == create_data.filename)
    )
    exist_file = result.scalar_one_or_none()
    if exist_file:
        logger.debug(f"File already exists: {create_data.filename}")
        db_file = await update_file(
            db=db,
            update_data=file_schemas.FileUpdate(
                file_id=exist_file.id,
                user_id=create_data.user_id,
                filename=create_data.filename,
                minio_path=create_data.minio_path,
                size=create_data.size,
            ),
        )
        return db_file

    db_file = file_models.File(
        user_id=create_data.user_id,
        minio_path=create_data.minio_path,
        filename=create_data.filename,
        size=create_data.size,
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


async def update_file(db: AsyncSession, update_data: file_schemas.FileUpdate):
    """
    更新文件记录
    """
    result = await db.execute(
        select(file_models.File).where(file_models.File.id == update_data.file_id)
    )
    db_file = result.scalar_one_or_none()

    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件未找到")
    update_data = update_data.model_dump(exclude_unset=True)
    try:
        for key, value in update_data.items():
            setattr(db_file, key, value)
        await db.commit()
        await db.refresh(db_file)
        return db_file
    except Exception as exc:
        await db.rollback()
        logger.error(f"Error updating file: {exc}")
        raise exc
