from typing import List

from sqlalchemy.exc import IntegrityError 

from models.models import Menu, SubMenu, Dish
from ..schemas import DishCreate
from .base_repository import BaseRepository


class DishRepository(BaseRepository):
    """Репозиторий для модели Dish"""
    def get_dish_list(
            self, 
            menu_id: int, 
            submenu_id: int
        ) -> List[Dish]:
        """Возвращает список блюд из подменю"""
        return self.session.query(Dish).\
            join(SubMenu, Dish.submenu_id == submenu_id).\
            join(Menu, SubMenu.menu_id == menu_id).all()
    

    def create_dish(
            self, 
            new_dish: DishCreate, 
            submenu_id: int
        ) -> Dish:
        """Создает блюдо"""
        dish_obj = Dish(**new_dish.model_dump())
        dish_obj.submenu_id = submenu_id
        self.session.add(dish_obj)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise IntegrityError
        return dish_obj


    def get_dish_by_id(
            self, menu_id: int, 
            submenu_id: int, dish_id: int
        ) -> Dish:
        """Возвращает блюдо"""
        return self.session.query(Dish).\
            join(SubMenu, Dish.submenu_id == submenu_id).\
            join(Menu, SubMenu.menu_id == menu_id).\
            filter(Dish.id == dish_id).one()


    def update_dish_by_id(
            self, menu_id: int, submenu_id: int, 
            dish_id: int, item: DishCreate
        ) -> Dish:
        """Обновляет блюдо"""
        dish_obj = self.get_dish_by_id(menu_id, submenu_id, dish_id)
        for key, value in item.model_dump().items():
            setattr(dish_obj, key, value)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
        return dish_obj   


    def delete_dish_by_id(
            self, menu_id: int, 
            submenu_id: int, dish_id: int
        ) -> None:
        """Удаляет блюдо"""
        dish_obj = self.get_dish_by_id(menu_id, submenu_id, dish_id)
        self.session.delete(dish_obj)
        self.session.commit()

    