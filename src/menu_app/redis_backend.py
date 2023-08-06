import pickle
from typing import List, Optional

import redis

from models.models import Menu, SubMenu, Dish
from config import REDIS_HOST, REDIS_PORT


class RedisBackend:

    TTL_CACHE = 60 * 60 * 24

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=0):
        self.__redis_cli = redis.Redis(host, port, db)
        

    def get_menu(self, menu_id: int) -> Optional[Menu]:
        """Возвращает объект menu из кеша"""
        menu_obj = self.__redis_cli.get(f'menu:{menu_id}')
        if menu_obj is None: 
            return None
        return pickle.loads(menu_obj)
    

    def get_submenu(self, submenu_id: int) -> Optional[SubMenu]:
        """Возвращает объект submenu из кеша"""
        submenu_obj = self.__redis_cli.\
            get(f'submenu:{submenu_id}')
        if submenu_obj is None: 
            return None
        return pickle.loads(submenu_obj)


    def get_dish(self, dish_id: int) -> Optional[Dish]:
        """Возвращает объект dish из кеша"""
        dish_obj = self.__redis_cli.get(f'dish:{dish_id}')
        if dish_obj is None: 
            return None
        return pickle.loads(dish_obj)
    

    def get_menu_list(self) -> Optional[List[Menu]]:
        """Возвращает список объектов menu из кеша"""
        menu_list = self.__redis_cli.get('menu_list')
        if menu_list is None:
            return None
        return pickle.loads(menu_list)
    

    def get_submenu_list(self, menu_id: int)\
          -> Optional[List[SubMenu]]:
        """
        Возвращает список объектов submenu, 
        которые относятся к объекту menu, из кеша
        """
        submenu_list = self.__redis_cli.\
            get(f'submenu_list:{menu_id}')
        if submenu_list is None:
            return None
        return pickle.loads(submenu_list)


    def get_dish_list(self, submenu_id: int) \
        -> Optional[List[Dish]]:
        """
        Возвращает список объектов dish,
        которые относятся к объекту submenu, из кеша
        """
        dish_list = self.__redis_cli.\
            get(f'dish_list:{submenu_id}') 
        if dish_list is None:
            return None
        return pickle.loads(dish_list)


    def delete_menu(self, menu_id: int) -> int:
        """
        Удаляет объект menu, список объектов menu
        и связанные объекты из кеша
        """
        self.delete_menu_list()
        self.delete_all_submenus()
        self.delete_all_dishes()
        return self.__redis_cli.delete(f'menu:{menu_id}')
    

    def delete_submenu(self, submenu_id: int) -> int:
        """
        Удаляет объект submenu и список объектов submenu из кеша.
        Также вызывает метод delete_menu 
        для связанного объекта menu.
        """
        submenu_obj = self.get_submenu(submenu_id)
        if submenu_obj is None:
            return None
        self.delete_menu(submenu_obj.menu_id)
        self.delete_submenu_list(submenu_obj.menu_id)
        self.delete_all_dishes()
        return self.__redis_cli.delete(f'submenu:{submenu_id}')


    def delete_dish(self, dish_id: int) -> int:
        """
        Удаляет объект dish и список объектов dish из кеша.
        Также вызывает метод delete_submenu 
        для связанного объекта submenu.
        """
        dish_obj = self.get_dish(dish_id)
        if dish_obj is None:
            return None
        self.delete_dish_list(dish_obj.submenu_id)
        self.delete_submenu(dish_obj.id)
        return self.__redis_cli.delete(f'dish:{dish_id}')


    def delete_menu_list(self) -> int:
        """Удаляет список объектов menu из кеша"""
        return self.__redis_cli.delete('menu_list')
    

    def delete_submenu_list(self, menu_id: int) -> int:
        """
        Удаляет список объектов submenu, 
        которые относятся к объекту menu, из кеша
        """
        return self.__redis_cli.delete(f'submenu_list:{menu_id}')


    def delete_dish_list(self, submenu_id: int) -> int:
        """
        Удаляет список объектов dish,
        которые относятся к объекту submenu,из кеша
        """
        return self.__redis_cli.delete(f'dish_list:{submenu_id}') 
    

    def set_menu(self, menu_obj: Menu) -> None:
        """
        Сохраняет в кеше объект menu 
        и удаляет неактуальный кеш
        """
        self.delete_menu(menu_obj.id)
        self.__redis_cli.setex(
            name=f'menu:{menu_obj.id}',
            value=pickle.dumps(menu_obj),
            time=self.TTL_CACHE
        )


    def set_submenu(self, submenu_obj: SubMenu) -> None:
        """
        Сохраняет в кеше объект submenu 
        и удаляет неактуальный кеш
        """
        self.delete_submenu(submenu_obj.id)
        self.__redis_cli.setex(
            name=f'submenu:{submenu_obj.id}',
            value=pickle.dumps(submenu_obj),
            time=self.TTL_CACHE
        )


    def set_dish(self, dish_obj: Dish) -> None:
        """
        Сохраняет в кеше объект dish 
        и удаляет неактуальный кеш
        """
        self.delete_dish(dish_obj.id)
        self.__redis_cli.setex(
            name=f'dish:{dish_obj.id}',
            value=pickle.dumps(dish_obj),
            time=self.TTL_CACHE
        )


    def set_menu_list(self, menu_list: List[Menu]) -> None:
        """Сохраняет в кеше список объектов menu"""
        self.__redis_cli.setex(
            name='menu_list',
            value=pickle.dumps(menu_list),
            time=self.TTL_CACHE
        )


    def set_submenu_list(
            self, 
            submenu_list: List[SubMenu], 
            menu_id: int
        ) -> None:
        """
        Сохраняет в кеше список объектов submenu, 
        которые относятся к объекту menu
        """
        self.__redis_cli.setex(
            name=f'submenu_list:{menu_id}',
            value=pickle.dumps(submenu_list),
            time=self.TTL_CACHE
        )

    
    def set_dish_list(
            self, 
            dish_list: List[Dish], 
            submenu_id: int
        ) -> None:
        """
        Сохраняет в кеше список объектов dish, 
        которые относятся к объекту submenu
        """
        self.__redis_cli.setex(
            name=f'dish_list:{submenu_id}',
            value=pickle.dumps(dish_list),
            time=self.TTL_CACHE
        )


    def delete_all_submenus(self) -> None:
        """Удаляет все подменю"""
        submenu_keys = self.__redis_cli.keys('submenu:*')
        submenu_keys += self.__redis_cli.keys('submenu_list:*')
        if not submenu_keys:
            return None
        self.__redis_cli.delete(*submenu_keys)


    def delete_all_dishes(self) -> None:
        """Удаляет все блюда"""
        dish_keys = self.__redis_cli.keys('dish:*') 
        dish_keys += self.__redis_cli.keys('dish_list:*') 
        if not dish_keys:
            return None
        self.__redis_cli.delete(*dish_keys) 


    def flushdb(self) -> None:
        """Очищает всю базу данных"""
        self.__redis_cli.flushdb()