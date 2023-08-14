from fastapi import BackgroundTasks, Depends

from menu_app.redis_backend import RedisBackend
from menu_app.repositories.menu_repository import MenuRepository
from menu_app.schemas import MenuCreate
from models.models import Menu


class MenuService:
    """
    Сервис, объединяющий работу MenuRepository и RedisBackend
    """

    def __init__(
            self,
            background_tasks: BackgroundTasks,
            menu_repository: MenuRepository = Depends(MenuRepository),
    ) -> None:
        self.__menu_repository = menu_repository
        self.__redis_cli = RedisBackend()
        self.__background_tasks = background_tasks

    async def get_all_list(self) -> list[Menu]:
        all_list = await self.__menu_repository.get_all_list()
        await self.__redis_cli.set_all_list(all_list)
        return all_list

    async def get_menu_list_with_counts(self) -> list[Menu]:
        menu_list = await self.__redis_cli.get_menu_list()
        if menu_list is None:
            menu_list = await self.__menu_repository.\
                get_menu_list_with_counts()
            await self.__redis_cli.set_menu_list(menu_list)
        return menu_list

    async def create_menu(
        self,
        new_menu: MenuCreate,
    ) -> Menu:
        menu_obj = await self.__menu_repository.create_menu(new_menu)
        self.__background_tasks.add_task(self.__redis_cli.delete_menu_list)
        return menu_obj

    async def get_menu_with_counts(self, menu_id: int) -> Menu:
        menu_obj = await self.__redis_cli.get_menu(menu_id)
        if menu_obj is None:
            menu_obj = await self.__menu_repository.\
                get_menu_with_counts(menu_id)
            await self.__redis_cli.set_menu(menu_obj)
        return menu_obj

    async def update_menu_by_id(
        self,
        menu_id: int,
        menu: MenuCreate,
    ) -> Menu:
        menu_obj = await self.__menu_repository.\
            update_menu_by_id(menu_id, menu)
        self.__background_tasks.add_task(self.__redis_cli.delete_menu, menu_id)
        return menu_obj

    async def delete_menu_by_id(
        self,
        menu_id,
    ) -> None:
        await self.__menu_repository.delete_menu_by_id(menu_id)
        self.__background_tasks.add_task(self.__redis_cli.delete_menu, menu_id)
