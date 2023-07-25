from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

from models.models import Dish, SubMenu

from ..schemas import SubMenuCreate
from .base_repository import BaseRepository


class SubMenuRepository(BaseRepository):
    """"Репозиторий для модели SubMenu"""

    async def get_submenu_list_with_dishes_count(
        self,
        menu_id: int
    ) -> list[SubMenu]:
        """
        Возвращает список всех подменю
        с количеством блюд в каждом подменю
        """
        submenus_with_dishes_count = await self.session.execute(
            select(SubMenu, func.count(Dish.id)).
            select_from(SubMenu).
            filter(SubMenu.menu_id == menu_id).
            outerjoin(Dish, SubMenu.id == Dish.submenu_id).
            group_by(SubMenu.id).order_by(SubMenu.id)
        )
        submenus = []
        for submenu_obj, dishes_count in submenus_with_dishes_count:
            setattr(submenu_obj, 'dishes_count', dishes_count)
            submenus.append(submenu_obj)
        return submenus

    async def create_submenu(
        self,
        new_submenu: SubMenuCreate,
        menu_id: int
    ) -> SubMenu:
        """Создает подменю"""
        submenu_obj = SubMenu(**new_submenu.model_dump())
        submenu_obj.menu_id = menu_id
        self.session.add(submenu_obj)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError('Ошибка при сохранении объекта')
        return submenu_obj

    async def get_submenu_by_id(
        self, menu_id: int,
        submenu_id: int
    ) -> SubMenu:
        """Возвращает подменю"""
        result = await self.session.execute(
            select(SubMenu).
            filter(
                SubMenu.id == submenu_id,
                SubMenu.menu_id == menu_id
            )
        )
        return result.one()[0]

    async def get_submenu_with_dishes_count(
        self, menu_id: int,
        submenu_id: int
    ) -> SubMenu:
        """Возвращает объект подменю с количеством блюд"""
        submenu_obj = await self.get_submenu_by_id(menu_id, submenu_id)
        dishes_count = await self.get_count_dishes_in_submenu(submenu_id)
        setattr(submenu_obj, 'dishes_count', dishes_count)
        return submenu_obj

    async def update_submenu_by_id(
        self,
        menu_id: int,
        submenu_id: int,
        item: SubMenuCreate
    ) -> SubMenu:
        """Обновляет подменю"""
        submenu_obj = await self.get_submenu_by_id(menu_id, submenu_id)
        for key, value in item.model_dump().items():
            setattr(submenu_obj, key, value)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError('Ошибка при сохранении объекта')
        return await self.get_submenu_with_dishes_count(menu_id, submenu_id)

    async def delete_submenu_by_id(
        self,
        menu_id: int,
        submenu_id: int
    ) -> None:
        """Удаляет подменю"""
        submenu_obj = await self.get_submenu_by_id(menu_id, submenu_id)
        await self.session.delete(submenu_obj)
        await self.session.commit()

    async def get_count_dishes_in_submenu(self, submenu_id: int) -> int:
        """Возвращает количество блюд в подменю"""
        result = await self.session.execute(
            select(func.count(Dish.id)).
            filter(Dish.submenu_id == submenu_id)
        )
        return result.scalar()
