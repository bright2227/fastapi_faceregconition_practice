import asyncio
import os
from pathlib import Path

import pytest
from app.db import SQLModel, get_session
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


PSQL_URL, DB_NAME =  os.environ.get("DATABASE_URL").rsplit("/",1)
TEST_DB_NAME = f"{DB_NAME}_testing"


engine = create_async_engine(f"{PSQL_URL}/{DB_NAME}", echo=True, future=True, execution_options={"isolation_level": "AUTOCOMMIT"},)
engine_testing = create_async_engine(f"{PSQL_URL}/{TEST_DB_NAME}", echo=True, future=True)


async def create_testdb():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        db_exists = await session.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'"))
        if not db_exists.scalar():
            await session.execute(text(f"CREATE DATABASE {TEST_DB_NAME}") )


async def drop_testdb():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await session.execute(text(f"DROP DATABASE {TEST_DB_NAME}"))

    await engine.dispose()


async def create_testtalbe():
    async with engine_testing.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_testtalbe():
    async with engine_testing.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine_testing.dispose()


async def get_session_testing() -> AsyncSession:
    async_session = sessionmaker(engine_testing, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
app.dependency_overrides[get_session] = get_session_testing


client = TestClient(app)
loop = asyncio.get_event_loop()


@pytest.fixture(scope="session")
def test_db():
    loop.run_until_complete(create_testdb())
    yield
    loop.run_until_complete(drop_testdb())


@pytest.fixture(scope="module")
def test_client(test_db):
    loop.run_until_complete(create_testtalbe())
    yield client
    loop.run_until_complete(drop_testtalbe())


@pytest.fixture(scope="session")
def test_pic_addr():
    return Path("./tests/test_pics/")
