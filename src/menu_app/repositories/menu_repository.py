from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func

from models.models import Dish, Menu, SubMenu

from ..schemas import MenuCreate
from .base_repository import BaseRepository


class MenuRepository(BaseRepository):
    """Репозиторий для модели Menu"""

    async def get_menu_list_with_counts(self) -> list[Menu]:
        """
        Возвращает список всех меню
        с количеством блюд и подменю в каждом меню
        """
        menus_with_dishes_count = await self.session.execute(
            select(Menu, func.count(Dish.id)).
            select_from(Menu).
            outerjoin(SubMenu, Menu.id == SubMenu.menu_id).
            outerjoin(Dish, SubMenu.id == Dish.submenu_id).
            group_by(Menu.id).order_by(Menu.id)
        )

        menus = []
        submenus_count = await self.get_submenus_count_for_menu_list()

        for menu_obj, dishes_count in menus_with_dishes_count:
            setattr(menu_obj, 'dishes_count', dishes_count)
            setattr(menu_obj, 'submenus_count', submenus_count[menu_obj.id])
            menus.append(menu_obj)
        return menus

    async def get_submenus_count_for_menu_list(self)\
            -> dict[int, int]:
        """Возвращает количество подменю во всех меню"""
        query_result = await self.session.execute(
            select(Menu.id, func.count(SubMenu.menu_id)).
            select_from(Menu).
            outerjoin(SubMenu, Menu.id == SubMenu.menu_id).
            group_by(Menu.id).order_by(Menu.id)
        )
        result_dict = {}  # ключ - menu_id, значение - количество подменю
        for key, value in query_result:
            result_dict[key] = value
        return result_dict

    async def create_menu(self, new_menu: MenuCreate) -> Menu:
        """Создает меню"""
        menu_obj = Menu(**new_menu.model_dump())
        self.session.add(menu_obj)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError('Ошибка при сохранении объекта')

        return menu_obj

    async def get_menu_by_id(self, menu_id: int) -> Menu:
        """Возвращает меню"""
        result = await self.session.execute(
            select(Menu).
            filter(Menu.id == menu_id)
        )
        return result.one()[0]

    async def get_menu_with_counts(self, menu_id: int) -> Menu:
        """
        Возвращает объект меню
        с количеством блюд и количеством меню
        """
        menu_obj = await self.get_menu_by_id(menu_id)
        dishes_count = await self.get_dishes_count_in_menu(menu_id)
        submenus_count = await self.get_submenus_count_in_menu(menu_id)

        menu_obj.dishes_count = dishes_count
        menu_obj.submenus_count = submenus_count
        return menu_obj

    async def get_submenus_count_in_menu(self, menu_id: int) -> int:
        """Возвращает количество подменю в меню"""
        result = await self.session.execute(
            select(func.count(SubMenu.menu_id)).
            select_from(SubMenu).
            filter(SubMenu.menu_id == menu_id)
        )
        return result.scalar()

    async def update_menu_by_id(
        self,
        menu_id: int,
        item: MenuCreate
    ) -> Menu:
        """Обновляет меню"""
        menu_obj = await self.get_menu_by_id(menu_id)
        for key, value in item.model_dump().items():
            setattr(menu_obj, key, value)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError('Ошибка при сохранении объекта')
        return await self.get_menu_with_counts(menu_id)

    async def delete_menu_by_id(self, menu_id: int) -> None:
        """Удаляет меню"""
        menu_obj = await self.get_menu_by_id(menu_id)
        await self.session.delete(menu_obj)
        await self.session.commit()

    async def get_dishes_count_in_menu(self, menu_id: int) -> int:
        """Возвращает количество блюд в меню"""
        result = await self.session.execute(
            select(func.count(Dish.id)).
            select_from(Menu).
            outerjoin(SubMenu, Menu.id == SubMenu.menu_id).
            outerjoin(Dish, SubMenu.id == Dish.submenu_id).
            filter(Menu.id == menu_id)
        )
        return result.scalar()

    async def get_all_list(self):
        """Возвращает все записи"""
        menus = await self.session.execute(
            select(Menu).
            options(
                joinedload(Menu.submenus).
                joinedload(SubMenu.dishes)
            )
        )
        result = [_tuple[0] for _tuple in menus.unique().all()]
        return result
