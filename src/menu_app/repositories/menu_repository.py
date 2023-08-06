from typing import List, Dict

from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError 

from models.models import Menu, SubMenu, Dish
from ..schemas import MenuCreate
from .base_repository import BaseRepository


class MenuRepository(BaseRepository):
    """Репозиторий для модели Menu"""
    def get_menu_list_with_counts(self) -> List[Menu]:
        """
        Возвращает список всех меню 
        с количеством блюд и подменю в каждом меню
        """
        menus_with_dishes_count = self.session.\
            query(Menu, func.count(Dish.id)).\
            select_from(Menu).\
            outerjoin(SubMenu, Menu.id == SubMenu.menu_id).\
            outerjoin(Dish, SubMenu.id == Dish.submenu_id).\
            group_by(Menu.id).order_by(Menu.id)
        
        menus = []
        submenus_count = self.get_submenus_count_for_menu_list()

        for menu_obj, dishes_count in menus_with_dishes_count:
            setattr(menu_obj, 'dishes_count', dishes_count)
            setattr(menu_obj, 'submenus_count', submenus_count[menu_obj.id])
            menus.append(menu_obj)
        return menus
    

    def get_submenus_count_for_menu_list(self)\
        -> Dict[int, int]:
        """Возвращает количество подменю во всех меню"""
        query_result = self.session.\
            query(Menu.id, func.count(SubMenu.menu_id)).\
            select_from(Menu).\
            outerjoin(SubMenu, Menu.id == SubMenu.menu_id).\
            group_by(Menu.id).order_by(Menu.id)
        result_dict = {}  # ключ - menu_id, значение - количество подменю
        for key, value in query_result:
            result_dict[key] = value
        return result_dict
    

    def create_menu(self, new_menu: MenuCreate) -> Menu:
        """Создает меню"""
        menu_obj = Menu(**new_menu.model_dump())
        self.session.add(menu_obj)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise IntegrityError

        return menu_obj
    

    def get_menu_by_id(self, menu_id: int) -> Menu:
        """Возвращает меню"""
        return self.session.query(Menu).\
                filter(Menu.id == menu_id).one()
    

    def get_menu_with_counts(self, menu_id: int) -> Menu:
        """
        Возвращает объект меню 
        с количеством блюд и количеством меню
        """
        menu_obj = self.get_menu_by_id(menu_id)

        dishes_count = self.get_dishes_count_in_menu(menu_id)
        submenus_count = self.get_submenus_count_in_menu(menu_id)

        setattr(menu_obj, 'dishes_count', dishes_count)
        setattr(menu_obj, 'submenus_count', submenus_count)
        return menu_obj


    def get_submenus_count_in_menu(self, menu_id: int) -> int:
        """Возвращает количество подменю в меню"""
        return self.session.query(func.count(SubMenu.menu_id)).\
                    select_from(SubMenu).\
                        filter(SubMenu.menu_id == menu_id).scalar()


    def update_menu_by_id(self,menu_id: int, item: MenuCreate) -> Menu:
        """Обновляет меню"""
        menu_obj = self.get_menu_by_id(menu_id)
        for key, value in item.model_dump().items():
            setattr(menu_obj, key, value)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise IntegrityError
        return self.get_menu_with_counts(menu_id)
    

    def delete_menu_by_id(self, menu_id: int) -> None:
        """Удаляет меню"""
        menu_obj = self.get_menu_by_id(menu_id)
        self.session.delete(menu_obj)
        self.session.commit()


    def get_dishes_count_in_menu(self, menu_id: int) -> int:
        """Возвращает количество блюд в меню"""
        return self.session.query(func.count(Dish.id)).\
            select_from(Menu).\
                outerjoin(SubMenu, Menu.id == SubMenu.menu_id).\
                    outerjoin(Dish, SubMenu.id == Dish.submenu_id).\
                        filter(Menu.id == menu_id).scalar()