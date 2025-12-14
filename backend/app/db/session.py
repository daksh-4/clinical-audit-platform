"""
Database session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.is_development,
    future=True,
    pool_pre_ping=True,
    poolclass=NullPool if settings.is_development else None,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency for getting database sessions.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
