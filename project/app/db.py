import asyncio
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlmodel import SQLModel


DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True, future=True)


async def check_db_alive():
    async with engine.begin() as conn:
        for _ in range(5):
            await conn.execute(text(""" SELECT 1; """))
            await asyncio.sleep(1)


async def close_db():
    await engine.dispose()


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
