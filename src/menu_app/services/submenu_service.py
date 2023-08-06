from typing import List

from fastapi import Depends

from menu_app.repositories.submenu_repository import SubMenuRepository
from menu_app.redis_backend import RedisBackend
from menu_app.schemas import SubMenuCreate
from models.models import SubMenu


class SubMenuService:
    """
    Сервис, объединяющий работу SubMenuRepository и RedisBackend.
    Методы имеют такую же сигнатуру, что и методы SubMenuRepository,
    но также выполняют работу с кешированием, используя RedisBackend.
    """
    def __init__(
            self, 
            submenu_repository: SubMenuRepository =\
                  Depends(SubMenuRepository),
    ) -> None:
        self.__submenu_repository = submenu_repository
        self.__redis_cli = RedisBackend()

    
    def get_submenu_list_with_dishes_count(
            self, 
            menu_id: int
        ) -> List[SubMenu]:
        submenu_list = self.__redis_cli.get_submenu_list(menu_id)
        if not submenu_list:
            submenu_list = self.__submenu_repository.\
            get_submenu_list_with_dishes_count(menu_id)
            self.__redis_cli.set_submenu_list(submenu_list, menu_id)
        return submenu_list
        

    def create_submenu(
            self,
            new_submenu: SubMenuCreate,
            menu_id: int
        ) -> SubMenu:
        submenu_obj = self.__submenu_repository.create_submenu(
            new_submenu,
            menu_id
        )
        self.__redis_cli.delete_menu(submenu_obj.menu_id)
        return submenu_obj


    def get_submenu_with_dishes_count(
            self,
            menu_id: int,
            submenu_id: int
        ) -> SubMenu:
        submenu_obj = self.__redis_cli.get_submenu(submenu_id)
        if not submenu_obj:
            submenu_obj = self.__submenu_repository.\
                get_submenu_with_dishes_count(menu_id, submenu_id)
            self.__redis_cli.set_submenu(submenu_obj)
        return submenu_obj


    def update_submenu_by_id(
            self, 
            menu_id: int,
            submenu_id: int,
            item: SubMenuCreate
        ) -> SubMenu:
        submenu_obj = self.__submenu_repository.\
            update_submenu_by_id(menu_id, submenu_id, item)
        self.__redis_cli.delete_submenu(submenu_id)
        return submenu_obj


    def delete_submenu_by_id(
            self,
            menu_id: int,
            submenu_id: int,
        ) -> None:
        self.__submenu_repository.\
            delete_submenu_by_id(menu_id, submenu_id)
        self.__redis_cli.delete_submenu(submenu_id)
