from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert

from ...models.knowledge_item import KnowledgeItem
from ...schemas.knowledge_item import ItemCreate


async def create_knowledge_item(db: AsyncSession, knowledge_item: ItemCreate):
    """
    创建知识项
    """
    db_knowledge_item = KnowledgeItem(**knowledge_item.dict())
    db.add(db_knowledge_item)
    await db.commit()
    await db.refresh(db_knowledge_item)
    return db_knowledge_item


async def get_knowledge_items_by_user(db: AsyncSession, user_id: int):
    """
    根据用户ID获取知识项
    """
    result = await db.execute(
        select(KnowledgeItem).where(KnowledgeItem.user_id == user_id)
    )
    return result.scalars().all()


async def get_knowledge_item(db: AsyncSession, knowledge_item_id: int):
    """
    根据ID获取知识项
    """
    result = await db.execute(
        select(KnowledgeItem).where(KnowledgeItem.id == knowledge_item_id)
    )
    return result.scalar_one_or_none()
