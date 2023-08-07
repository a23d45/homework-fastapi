from fastapi import Depends

from menu_app.redis_backend import RedisBackend
from menu_app.repositories.dish_repository import DishRepository
from menu_app.schemas import DishCreate
from models.models import Dish


class DishService:
    """
    Сервис, объединяющий работу DishRepository и RedisBackend.
    Методы имеют такую же сигнатуру, что и методы DishRepository,
    но также выполняют работу с кешированием, используя RedisBackend.
    """

    def __init__(
            self,
            dish_repository: DishRepository = Depends(DishRepository),
    ) -> None:
        self.__dish_repository = dish_repository
        self.__redis_cli = RedisBackend()

    def get_dish_list(
        self,
        menu_id: int,
        submenu_id: int
    ) -> list[Dish]:
        dish_list = self.__redis_cli.get_dish_list(submenu_id)
        if not dish_list:
            dish_list = self.__dish_repository.\
                get_dish_list(menu_id, submenu_id)
        self.__redis_cli.set_dish_list(dish_list, submenu_id)
        return dish_list

    def create_dish(
        self,
        new_dish: DishCreate,
        submenu_id: int
    ) -> Dish:
        dish_obj = self.__dish_repository.\
            create_dish(new_dish, submenu_id)
        self.__redis_cli.delete_dish(dish_obj.id)
        return dish_obj

    def get_dish_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int,
    ) -> Dish:
        dish_obj = self.__redis_cli.get_dish(dish_id)
        if not dish_obj:
            dish_obj = self.__dish_repository.\
                get_dish_by_id(menu_id, submenu_id, dish_id)
            self.__redis_cli.set_dish(dish_obj)
        return dish_obj

    def update_dish_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int,
        item: DishCreate,
    ) -> Dish:
        dish_obj = self.__dish_repository.\
            update_dish_by_id(menu_id, submenu_id, dish_id, item)
        self.__redis_cli.delete_dish(dish_id)
        return dish_obj

    def delete_dish_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int
    ) -> None:
        self.__dish_repository.\
            delete_dish_by_id(menu_id, submenu_id, dish_id)
        self.__redis_cli.delete_dish(dish_id)
