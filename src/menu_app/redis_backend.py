import pickle

from redis import asyncio as aioredis

from config import REDIS_HOST, REDIS_PORT
from models.models import Dish, Menu, SubMenu


class RedisBackend:

    TTL_CACHE = 60 * 60 * 24

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=0):
        url = f'redis://{host}:{port}'
        self.__redis_cli = aioredis.from_url(url)

    async def get_menu(self, menu_id: int) -> Menu | None:
        """Возвращает объект menu из кеша"""
        menu_var = self.__get_menu_var_name(menu_id)
        menu_obj = await self.__redis_cli.get(menu_var)
        if menu_obj is None:
            return None
        return pickle.loads(menu_obj)

    async def get_submenu(
        self,
        menu_id: int,
        submenu_id: int
    ) -> SubMenu | None:
        """Возвращает объект submenu из кеша"""
        submenu_var = self.\
            __get_submenu_var_name(menu_id, submenu_id)
        submenu_obj = await self.__redis_cli.get(submenu_var)
        if submenu_obj is None:
            return None
        return pickle.loads(submenu_obj)

    async def get_dish(
            self,
            menu_id: int,
            submenu_id: int,
            dish_id: int
    ) -> Dish | None:
        """Возвращает объект dish из кеша"""
        dish_var = self.\
            __get_dish_var_name(menu_id, submenu_id, dish_id)
        dish_obj = await self.__redis_cli.get(dish_var)
        if dish_obj is None:
            return None
        return pickle.loads(dish_obj)

    async def get_menu_list(self) -> list[Menu] | None:
        """Возвращает список объектов menu из кеша"""
        menu_list = await self.__redis_cli.get('menu_list')
        if menu_list is None:
            return None
        return pickle.loads(menu_list)

    async def get_submenu_list(self, menu_id: int)\
            -> list[SubMenu] | None:
        """
        Возвращает список объектов submenu,
        которые относятся к объекту menu, из кеша
        """
        submenu_list = await self.__redis_cli.\
            get(f'submenu_list:{menu_id}')
        if submenu_list is None:
            return None
        return pickle.loads(submenu_list)

    async def get_dish_list(
        self,
        menu_id: int,
        submenu_id: int
    ) -> list[Dish] | None:
        """
        Возвращает список объектов dish,
        которые относятся к объекту submenu, из кеша
        """
        dish_list_var = self.\
            __get_dish_list_var_name(menu_id, submenu_id)
        dish_list = await self.__redis_cli.get(dish_list_var)
        if dish_list is None:
            return None
        return pickle.loads(dish_list)

    async def delete_menu(self, menu_id: int) -> None:
        """
        Удаляет объект menu, список объектов menu
        и связанные объекты из кеша
        """
        await self.delete_menu_list()
        await self.delete_submenu_list(menu_id)
        menu_var = self.__get_menu_var_name(menu_id)
        invalid_keys = await self.__redis_cli.keys(f'{menu_var}*')
        invalid_keys += await self.__redis_cli.\
            keys(f'dish_list:{menu_id}:*')
        if invalid_keys:
            await self.__redis_cli.delete(*invalid_keys)

    async def delete_submenu(
        self,
        menu_id: int,
        submenu_id: int
    ) -> None:
        """
        Удаляет объект submenu, список объектов submenu
        и связанные объекты из кеша
        """
        await self.delete_menu_list()
        await self.delete_submenu_list(menu_id)
        await self.delete_dish_list(menu_id, submenu_id)
        menu_var = self.__get_menu_var_name(menu_id)
        submenu_var = self.\
            __get_submenu_var_name(menu_id, submenu_id)

        invalid_keys = await self.__redis_cli.keys(f'{submenu_var}*')
        invalid_keys.append(menu_var)
        await self.__redis_cli.delete(*invalid_keys)

    async def delete_dish(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int
    ) -> None:
        """
        Удаляет объект dish, список объектов dish
        и связанные объекты из кеша
        """
        await self.delete_menu_list()
        await self.delete_submenu_list(menu_id)
        await self.delete_dish_list(menu_id, submenu_id)

        menu_var = self.__get_menu_var_name(menu_id)
        submenu_var = self.\
            __get_submenu_var_name(menu_id, submenu_id)
        dish_var = self.\
            __get_dish_var_name(menu_id, submenu_id, dish_id)

        await self.__redis_cli.delete(menu_var)
        await self.__redis_cli.delete(submenu_var)
        await self.__redis_cli.delete(dish_var)

    async def delete_menu_list(self) -> None:
        """Удаляет список объектов menu из кеша"""
        await self.delete_all_list()
        await self.__redis_cli.delete('menu_list')

    async def delete_submenu_list(self, menu_id: int) -> None:
        """
        Удаляет список объектов submenu,
        которые относятся к объекту menu, из кеша
        """
        await self.__redis_cli.delete(f'submenu_list:{menu_id}')

    async def delete_dish_list(
        self,
        menu_id: int,
        submenu_id: int
    ) -> None:
        """
        Удаляет список объектов dish,
        которые относятся к объекту submenu,из кеша
        """
        dish_list_var = self.\
            __get_dish_list_var_name(menu_id, submenu_id)
        await self.__redis_cli.delete(dish_list_var)

    async def set_menu(self, menu_obj: Menu) -> None:
        """
        Сохраняет в кеше объект menu
        и удаляет неактуальный кеш
        """
        await self.delete_menu(menu_obj.id)

        menu_var = self.__get_menu_var_name(menu_obj.id)
        await self.__redis_cli.setex(
            name=menu_var,
            value=pickle.dumps(menu_obj),
            time=self.TTL_CACHE
        )

    async def set_submenu(self, submenu_obj: SubMenu) -> None:
        """
        Сохраняет в кеше объект submenu
        и удаляет неактуальный кеш
        """
        await self.delete_submenu(submenu_obj.menu_id, submenu_obj.id)

        submenu_var = self.\
            __get_submenu_var_name(submenu_obj.menu_id, submenu_obj.id)
        await self.__redis_cli.setex(
            name=submenu_var,
            value=pickle.dumps(submenu_obj),
            time=self.TTL_CACHE
        )

    async def set_dish(self, dish_obj: Dish, menu_id: int) -> None:
        """
        Сохраняет в кеше объект dish
        и удаляет неактуальный кеш
        """
        submenu_id = dish_obj.submenu_id

        await self.delete_dish(menu_id, submenu_id, dish_obj.id)
        dish_var = self.\
            __get_dish_var_name(menu_id, submenu_id, dish_obj.id)
        await self.__redis_cli.setex(
            name=dish_var,
            value=pickle.dumps(dish_obj),
            time=self.TTL_CACHE
        )

    async def set_menu_list(self, menu_list: list[Menu]) -> None:
        """Сохраняет в кеше список объектов menu"""
        await self.__redis_cli.setex(
            name='menu_list',
            value=pickle.dumps(menu_list),
            time=self.TTL_CACHE
        )

    async def set_submenu_list(
        self,
        submenu_list: list[SubMenu],
        menu_id: int
    ) -> None:
        """
        Сохраняет в кеше список объектов submenu,
        которые относятся к объекту menu
        """
        await self.__redis_cli.setex(
            name=f'submenu_list:{menu_id}',
            value=pickle.dumps(submenu_list),
            time=self.TTL_CACHE
        )

    async def set_dish_list(
        self,
        dish_list: list[Dish],
        menu_id: int,
        submenu_id: int
    ) -> None:
        """
        Сохраняет в кеше список объектов dish,
        которые относятся к объекту submenu
        """
        dish_list_var = self.\
            __get_dish_list_var_name(menu_id, submenu_id)
        await self.__redis_cli.setex(
            name=dish_list_var,
            value=pickle.dumps(dish_list),
            time=self.TTL_CACHE
        )

    async def flushdb(self) -> None:
        """Очищает всю базу данных"""
        await self.__redis_cli.flushdb()

    async def get_all_list(self) -> list[Menu] | None:
        """Возвращает список объектов Menu со вложенными объектами"""
        result = await self.__redis_cli.get('all')
        if result is None:
            return None
        return pickle.loads(result)

    async def delete_all_list(self) -> None:
        """Удаляет список объектов Menu со вложенными объектами"""
        await self.__redis_cli.delete('all')

    async def set_all_list(self, all_list: list[Menu]) -> None:
        """Сохраняет список объектов Menu со вложенными объектами"""
        await self.__redis_cli.setex(
            name='all',
            value=pickle.dumps(all_list),
            time=self.TTL_CACHE
        )

    async def close_connection(self) -> None:
        """Закрывает подключение и очищает базу данных"""
        await self.flushdb()
        await self.__redis_cli.close()

    def __get_menu_var_name(self, menu_id: int) -> str:
        """Генерирует имя переменной для объекта menu"""
        return f'menu:{menu_id}'

    def __get_submenu_var_name(
        self,
        menu_id: int,
        submenu_id: int
    ) -> str:
        """Генерирует имя переменной для объекта submenu"""
        return f'menu:{menu_id}:submenu:{submenu_id}'

    def __get_dish_var_name(
        self,
        menu_id: int,
        submenu_id: int,
        dish_id: int
    ) -> str:
        """Генерирует имя переменной для объекта dish"""
        return f'menu:{menu_id}:submenu:{submenu_id}:dish:{dish_id}'

    def __get_dish_list_var_name(
        self,
        menu_id: int,
        submenu_id: int,
    ) -> str:
        """Генерирует имя переменной для списка dish_list"""
        return f'dish_list:{menu_id}:{submenu_id}'
