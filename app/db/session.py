from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,        
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def close_engine() -> None:
    await engine.dispose()


async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                yield session
        
        except Exception:
            await session.rollback()
            raise

