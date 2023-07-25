from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.models import Dish, Menu, SubMenu

from ..schemas import DishCreate
from .base_repository import BaseRepository


class DishRepository(BaseRepository):
    """Репозиторий для модели Dish"""

    async def get_dish_list(
        self,
        menu_id: int,
        submenu_id: int
    ) -> list[Dish]:
        """Возвращает список блюд из подменю"""
        result = await self.session.execute(
            select(Dish).
            join(SubMenu, Dish.submenu_id == submenu_id).
            join(Menu, SubMenu.menu_id == menu_id)
        )
        result = [_tuple[0] for _tuple in result.all()]
        return result

    async def create_dish(
        self,
        new_dish: DishCreate,
        submenu_id: int
    ) -> Dish:
        """Создает блюдо"""
        dish_obj = Dish(**new_dish.model_dump())
        dish_obj.submenu_id = submenu_id
        self.session.add(dish_obj)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError('Ошибка при сохранении объекта')
        return dish_obj

    async def get_dish_by_id(
        self, menu_id: int,
        submenu_id: int, dish_id: int
    ) -> Dish:
        """Возвращает блюдо"""
        result = await self.session.execute(
            select(Dish).
            join(SubMenu, Dish.submenu_id == submenu_id).
            join(Menu, SubMenu.menu_id == menu_id).
            filter(Dish.id == dish_id)
        )
        return result.one()[0]

    async def update_dish_by_id(
        self, menu_id: int, submenu_id: int,
        dish_id: int, item: DishCreate
    ) -> Dish:
        """Обновляет блюдо"""
        dish_obj = await self.get_dish_by_id(menu_id, submenu_id, dish_id)
        for key, value in item.model_dump().items():
            setattr(dish_obj, key, value)
        try:
            await self.session.commit()
        except IntegrityError:
            self.session.execute.rollback()
            raise ValueError('Ошибка при сохранении объекта')
        return dish_obj

    async def delete_dish_by_id(
        self, menu_id: int,
        submenu_id: int, dish_id: int
    ) -> None:
        """Удаляет блюдо"""
        dish_obj = await self.get_dish_by_id(menu_id, submenu_id, dish_id)
        await self.session.delete(dish_obj)
        await self.session.commit()
