from typing import List

from fastapi import Depends

from menu_app.repositories.menu_repository import MenuRepository
from menu_app.redis_backend import RedisBackend
from menu_app.schemas import MenuCreate
from models.models import Menu


class MenuService:
    """
    Сервис, объединяющий работу MenuRepository и RedisBackend.
    Методы имеют такую же сигнатуру, что и методы MenuRepository,
    но также выполняют работу с кешированием, используя RedisBackend.
    """
    def __init__(
            self, 
            menu_repository: MenuRepository = Depends(MenuRepository),
    ) -> None:
        self.__menu_repository = menu_repository
        self.__redis_cli = RedisBackend()


    def get_menu_list_with_counts(self) -> List[Menu]:
        menu_list = self.__redis_cli.get_menu_list()
        if not menu_list:
            menu_list = self.__menu_repository.\
                get_menu_list_with_counts()
            self.__redis_cli.set_menu_list(menu_list)
        return menu_list


    def create_menu(self, new_menu: MenuCreate) -> Menu:
        menu_obj = self.__menu_repository.create_menu(new_menu)
        self.__redis_cli.delete_menu_list()
        return menu_obj
    

    def get_menu_with_counts(self, menu_id: int) -> Menu:
        menu_obj = self.__redis_cli.get_menu(menu_id)
        if not menu_obj:
            menu_obj = self.__menu_repository.\
                get_menu_with_counts(menu_id)
            self.__redis_cli.set_menu(menu_obj)
        return menu_obj


    def update_menu_by_id(
            self, 
            menu_id: int, 
            menu: MenuCreate
    ) -> Menu:
        menu_obj = self.__menu_repository.\
            update_menu_by_id(menu_id, menu)
        self.__redis_cli.delete_menu(menu_id)
        return menu_obj
    

    def delete_menu_by_id(self, menu_id) -> None:
        self.__menu_repository.delete_menu_by_id(menu_id)
        self.__redis_cli.delete_menu(menu_id)


        