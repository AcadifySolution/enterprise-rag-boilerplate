from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Initialize async engine for pgvector database
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db_session():
    """
    Dependency generator yielding async db sessions.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
