from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE_URL

async_engine = create_async_engine(DATABASE_URL)
Session = async_sessionmaker(async_engine)

Base = declarative_base()


async def create_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    