from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session


class BaseRepository:
    """Базовый репозиторий для создания других репозиториев"""

    def __init__(
        self,
        session: AsyncSession = Depends(get_async_session)
    ) -> None:
        self.session = session
