from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL, MONGO_URI, MONGO_DB_NAME, DB_POOL_SIZE

engine = create_async_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=5,
    echo=False,
)

AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_mongo_db():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db


async def close_db_connections():
    await engine.dispose()
