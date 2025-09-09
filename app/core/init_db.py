from .database import Base, engine
from loguru import logger
from sqlalchemy import text

from ..models import User, KnowledgeItem, File, ChatHistory


def init_database():
    # create all tables
    try:
        # Try to enable pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        logger.info("Vector extension enabled successfully")
    except Exception as e:
        logger.warning(f"Could not enable vector extension: {e}")
        logger.warning("Please ensure pgvector extension is installed on your PostgreSQL server")
        logger.warning("Refer to https://github.com/pgvector/pgvector for installation instructions")
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.success("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        logger.error("If you see a 'type \"vector\" does not exist' error, please install pgvector extension")


if __name__ == "__main__":
    init_database()