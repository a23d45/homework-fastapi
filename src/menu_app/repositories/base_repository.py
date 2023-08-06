from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_session


class BaseRepository:
    """Базовый репозиторий для создания других репозиториев"""
    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session 