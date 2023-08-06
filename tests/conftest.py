import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import close_all_sessions

from src.main import app
from src.database import engine, get_session
from src.config import MODE
from src.models.models import Base, Menu, SubMenu, Dish
from src.menu_app.redis_backend import RedisBackend


@pytest.fixture(scope='session', autouse=True)
def setup_db():
    assert MODE == 'TEST'
    Base.metadata.drop_all(engine)
    redis_cli = RedisBackend()
    redis_cli.flushdb()
    Base.metadata.create_all(engine)
    yield   
    close_all_sessions()
    Base.metadata.drop_all(engine)
    redis_cli.flushdb()
    

@pytest.fixture(scope="module")
def client():
    yield TestClient(app)


@pytest.fixture(scope="module")
def current_menu():
    session = next(get_session())
    return session.query(Menu).one()


@pytest.fixture(scope="module")
def current_submenu():
    session = next(get_session())
    return session.query(SubMenu).one()


@pytest.fixture(scope="module")
def current_dish():
    session = next(get_session())
    return session.query(Dish).one()
