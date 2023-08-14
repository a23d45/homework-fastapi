from fastapi import BackgroundTasks, Depends

from menu_app.redis_backend import RedisBackend
from menu_app.repositories.submenu_repository import SubMenuRepository
from menu_app.schemas import SubMenuCreate
from models.models import SubMenu


class SubMenuService:
    """
    Сервис, объединяющий работу SubMenuRepository и RedisBackend
    """

    def __init__(
        self,
        background_tasks: BackgroundTasks,
        submenu_repository: SubMenuRepository = Depends(SubMenuRepository),
    ) -> None:
        self.__submenu_repository = submenu_repository
        self.__background_tasks = background_tasks
        self.__redis_cli = RedisBackend()

    async def get_submenu_list_with_dishes_count(
        self,
        menu_id: int
    ) -> list[SubMenu]:
        submenu_list = await self.__redis_cli.get_submenu_list(menu_id)
        if submenu_list is None:
            submenu_list = await self.__submenu_repository.\
                get_submenu_list_with_dishes_count(menu_id)
            await self.__redis_cli.set_submenu_list(submenu_list, menu_id)
        return submenu_list

    async def create_submenu(
        self,
        new_submenu: SubMenuCreate,
        menu_id: int,
    ) -> SubMenu:
        submenu_obj = await self.__submenu_repository.create_submenu(
            new_submenu,
            menu_id
        )
        self.__background_tasks.add_task(
            self.__redis_cli.delete_submenu, menu_id, submenu_obj.menu_id
        )
        return submenu_obj

    async def get_submenu_with_dishes_count(
        self,
        menu_id: int,
        submenu_id: int
    ) -> SubMenu:
        submenu_obj = await self.__redis_cli.\
            get_submenu(menu_id, submenu_id)
        if submenu_obj is None:
            submenu_obj = await self.__submenu_repository.\
                get_submenu_with_dishes_count(menu_id, submenu_id)
            await self.__redis_cli.set_submenu(submenu_obj)
        return submenu_obj

    async def update_submenu_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        item: SubMenuCreate,
    ) -> SubMenu:
        submenu_obj = await self.__submenu_repository.\
            update_submenu_by_id(menu_id, submenu_id, item)
        self.__background_tasks.add_task(
            self.__redis_cli.delete_submenu, menu_id, submenu_id
        )
        return submenu_obj

    async def delete_submenu_by_id(
        self,
        menu_id: int,
        submenu_id: int,
    ) -> None:
        await self.__submenu_repository.\
            delete_submenu_by_id(menu_id, submenu_id)
        self.__background_tasks.add_task(
            self.__redis_cli.delete_submenu, menu_id, submenu_id
        )
