from fastapi import BackgroundTasks, Depends

from menu_app.redis_backend import RedisBackend
from menu_app.repositories.dish_repository import DishRepository
from menu_app.schemas import DishCreate
from models.models import Dish


class DishService:
    """
    Сервис, объединяющий работу DishRepository и RedisBackend
    """

    def __init__(
            self,
            background_tasks: BackgroundTasks,
            dish_repository: DishRepository = Depends(DishRepository),
    ) -> None:
        self.__dish_repository = dish_repository
        self.__background_tasks = background_tasks
        self.__redis_cli = RedisBackend()

    async def get_dish_list(
        self,
        menu_id: int,
        submenu_id: int
    ) -> list[Dish]:
        dish_list = await self.__redis_cli.\
            get_dish_list(menu_id, submenu_id)
        if dish_list is None:
            dish_list = await self.__dish_repository.\
                get_dish_list(menu_id, submenu_id)
            await self.__redis_cli.\
                set_dish_list(dish_list, menu_id, submenu_id)
        return dish_list

    async def create_dish(
        self,
        new_dish: DishCreate,
        menu_id: int,
        submenu_id: int,
    ) -> Dish:
        dish_obj = await self.__dish_repository.\
            create_dish(new_dish, submenu_id)
        self.__background_tasks.add_task(
            self.__redis_cli.delete_dish, menu_id, submenu_id, dish_obj.id
        )
        return dish_obj

    async def get_dish_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int,
    ) -> Dish:
        dish_obj = await self.\
            __redis_cli.get_dish(menu_id, submenu_id, dish_id)
        if dish_obj is None:
            dish_obj = await self.__dish_repository.\
                get_dish_by_id(menu_id, submenu_id, dish_id)
            await self.__redis_cli.set_dish(dish_obj, menu_id)
        return dish_obj

    async def update_dish_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int,
        item: DishCreate,
    ) -> Dish:
        dish_obj = await self.__dish_repository.\
            update_dish_by_id(menu_id, submenu_id, dish_id, item)
        self.__background_tasks.add_task(
            self.__redis_cli.delete_dish, menu_id, submenu_id, dish_id
        )
        return dish_obj

    async def delete_dish_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int
    ) -> None:
        await self.__dish_repository.\
            delete_dish_by_id(menu_id, submenu_id, dish_id)
        self.__background_tasks.add_task(
            self.__redis_cli.delete_dish, menu_id, submenu_id, dish_id
        )
