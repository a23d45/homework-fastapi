import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import close_all_sessions, sessionmaker
from sqlalchemy.pool import NullPool

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, MODE
from src.database import get_async_session
from src.main import app
from src.menu_app.redis_backend import RedisBackend
from src.models.models import Base, Dish, Menu, SubMenu

DATABASE_URL_TEST =\
    f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine_test = create_async_engine(DATABASE_URL_TEST)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata = Base.metadata
metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def setup_db():
    assert MODE == 'TEST'
    redis_cli = RedisBackend()
    await redis_cli.flushdb()
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    yield
    await redis_cli.close_connection()
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope='module')
async def current_menu():
    session_generator = override_get_async_session()
    session = await anext(session_generator)
    menu_obj = await session.execute(select(Menu))
    yield menu_obj.one()[0]
    await session.close()


@pytest.fixture(scope='module')
async def current_submenu():
    session_generator = override_get_async_session()
    session = await anext(session_generator)
    submenu_obj = await session.execute(select(SubMenu))
    yield submenu_obj.one()[0]
    await session.close()


@pytest.fixture(scope='module')
async def current_dish():
    session_generator = override_get_async_session()
    session = await anext(session_generator)
    dish = await session.execute(select(Dish))
    yield dish.one()[0]
    await session.close()


@pytest.fixture(scope='session')
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
