from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

from models.models import Dish, SubMenu

from ..schemas import SubMenuCreate
from .base_repository import BaseRepository


class SubMenuRepository(BaseRepository):
    """"Репозиторий для модели SubMenu"""

    def get_submenu_list_with_dishes_count(
        self,
        menu_id: int
    ) -> list[SubMenu]:
        """
        Возвращает список всех подменю
        с количеством блюд в каждом подменю
        """
        submenus_with_dishes_count = self.session.\
            query(SubMenu, func.count(Dish.id)).\
            select_from(SubMenu).\
            filter(SubMenu.menu_id == menu_id).\
            outerjoin(Dish, SubMenu.id == Dish.submenu_id).\
            group_by(SubMenu.id).order_by(SubMenu.id)
        submenus = []
        for submenu_obj, dishes_count in submenus_with_dishes_count:
            setattr(submenu_obj, 'dishes_count', dishes_count)
            submenus.append(submenu_obj)
        return submenus

    def create_submenu(
        self,
        new_submenu: SubMenuCreate,
        menu_id: int
    ) -> SubMenu:
        """Создает подменю"""
        submenu_obj = SubMenu(**new_submenu.model_dump())
        submenu_obj.menu_id = menu_id
        self.session.add(submenu_obj)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise IntegrityError
        return submenu_obj

    def get_submenu_by_id(
        self, menu_id: int,
        submenu_id: int
    ) -> SubMenu:
        """Возвращает подменю"""
        return self.session.query(SubMenu).\
            filter(SubMenu.id == submenu_id,
                   SubMenu.menu_id == menu_id).one()

    def get_submenu_with_dishes_count(
        self, menu_id: int,
        submenu_id: int
    ) -> SubMenu:
        """Возвращает объект подменю с количеством блюд"""
        submenu_obj = self.get_submenu_by_id(menu_id, submenu_id)
        dishes_count = self.get_count_dishes_in_submenu(submenu_id)
        setattr(submenu_obj, 'dishes_count', dishes_count)
        return submenu_obj

    def update_submenu_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        item: SubMenuCreate
    ) -> SubMenu:
        """Обновляет подменю"""
        submenu_obj = self.get_submenu_by_id(menu_id, submenu_id)
        for key, value in item.model_dump().items():
            setattr(submenu_obj, key, value)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise IntegrityError
        return self.get_submenu_with_dishes_count(menu_id, submenu_id)

    def delete_submenu_by_id(
        self,
        menu_id: int,
        submenu_id: int
    ) -> None:
        """Удаляет подменю"""
        submenu_obj = self.get_submenu_by_id(menu_id, submenu_id)
        self.session.delete(submenu_obj)
        self.session.commit()

    def get_count_dishes_in_submenu(self, submenu_id: int) -> int:
        """Возвращает количество блюд в подменю"""
        return self.session.query(Dish).\
            filter(Dish.submenu_id == submenu_id).count()
