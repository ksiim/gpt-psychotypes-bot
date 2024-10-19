from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
Session = async_sessionmaker(engine)

Base = declarative_base()

async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
