import os

import pandas as pd

FILE_PATH = os.path.abspath('../admin/Menu.xlsx')


class ExcelBackend:
    """Парсит excel файл"""

    MENU_ID_COLUMN = 0
    MENU_TITLE_COLUMN = 1
    MENU_DESCRIPTION_COLUMN = 2

    SUBMENU_ID_COLUMN = 1
    SUBMENU_TITLE_COLUMN = 2
    SUBMENU_DESCRIPTION_COLUMN = 3

    DISH_ID_COLUMN = 2
    DISH_TITLE_COLUMN = 3
    DISH_DESCRIPTION_COLUMN = 4
    DISH_PRICE_COLUMN = 5

    def __init__(self, path=FILE_PATH) -> None:
        self.path = FILE_PATH
        self.df = pd.read_excel(
            io=self.path,
            header=None
        )
        self.excel_data = self.df.to_dict()

    def get_menu_id(self, cell_number: int) -> int:
        """Возвращает id меню"""
        return int(
            self.excel_data.get(
                self.MENU_ID_COLUMN
            ).get(cell_number)
        )

    def get_menu_description(self, cell_number: int) -> str:
        """Возвращает описание меню"""
        return self.excel_data.get(
            self.MENU_DESCRIPTION_COLUMN
        ).get(cell_number)

    def get_submenu_id(self, cell_number: int) -> int:
        """Возвращает id подменю"""
        return int(
            self.excel_data.get(
                self.SUBMENU_ID_COLUMN
            ).get(cell_number)
        )

    def get_submenu_description(self, cell_number: int) -> str:
        """Возвращает описание подменю"""
        return self.excel_data.get(
            self.SUBMENU_DESCRIPTION_COLUMN
        ).get(cell_number)

    def get_dish_id(self, cell_number: int) -> int:
        """Возвращает id блюда"""
        return int(
            self.excel_data.get(
                self.DISH_ID_COLUMN
            ).get(cell_number)
        )

    def get_dish_description(self, cell_number: int) -> str:
        """Возвращает описание блюда"""
        return self.excel_data.get(
            self.DISH_DESCRIPTION_COLUMN
        ).get(cell_number)

    def get_dish_price(self, cell_number: int) -> str:
        """Возвращает строку стоимости блюда"""
        return str(
            self.excel_data.get(
                self.DISH_PRICE_COLUMN
            ).get(cell_number)
        )

    def get_menus(self) -> list[dict]:
        """Возвращает список словарей меню"""
        menus_list = []
        menu_title_column = self.excel_data.get(self.MENU_TITLE_COLUMN)
        for cell_number, value in menu_title_column.items():
            if isinstance(value, str):
                menu_dict = {}
                menu_dict['id'] = self.get_menu_id(cell_number)
                menu_dict['title'] = value
                menu_dict['description'] =\
                    self.get_menu_description(cell_number)
                menus_list.append(menu_dict)
        return menus_list

    def get_submenus(self) -> list[dict]:
        """Возвращает список словарей подменю"""
        submenus_list = []
        submenu_title_column = self.excel_data.\
            get(self.SUBMENU_TITLE_COLUMN)
        left_column = self.excel_data.get(self.SUBMENU_TITLE_COLUMN - 1)

        current_menu_id = None
        for cell_number, value in submenu_title_column.items():
            left_cell = left_column.get(cell_number)

            if isinstance(value, str) and isinstance(left_cell, str):
                current_menu_id = self.get_menu_id(cell_number)

            if isinstance(value, str) and isinstance(left_cell, int):
                submenu_dict = {}
                submenu_dict['id'] =\
                    self.get_submenu_id(cell_number)
                submenu_dict['title'] = value
                submenu_dict['description'] =\
                    self.get_submenu_description(cell_number)
                submenu_dict['menu_id'] = current_menu_id
                submenus_list.append(submenu_dict)
        return submenus_list

    def get_dishes(self) -> list[dict]:
        """Возвращает список словарей блюд"""
        dishes_list = []
        dish_title_column = self.excel_data.\
            get(self.DISH_TITLE_COLUMN)
        left_column = self.excel_data.get(self.DISH_TITLE_COLUMN - 1)

        current_submenu_id = None
        for cell_number, value in dish_title_column.items():
            left_cell = left_column.get(cell_number)

            if isinstance(value, str) and isinstance(left_cell, str):
                current_submenu_id = self.get_submenu_id(cell_number)

            if isinstance(value, str) and isinstance(left_cell, int):
                dish_dict = {}
                dish_dict['id'] =\
                    self.get_dish_id(cell_number)
                dish_dict['title'] = value
                dish_dict['description'] =\
                    self.get_dish_description(cell_number)
                dish_dict['submenu_id'] = current_submenu_id
                dish_dict['price'] = self.get_dish_price(cell_number)
                dishes_list.append(dish_dict)
        return dishes_list
