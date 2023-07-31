from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from models.models import Menu, SubMenu, Dish
from .schemas import MenuCreate, SubMenuCreate, DishCreate


def get_menu_list_with_counts(session: Session):
    """
    Возвращает список всех меню 
    с количеством блюд и подменю в каждом меню
    """
    menus_with_dishes_count = session.query(Menu, func.count(Dish.id)).\
        select_from(Menu).\
        outerjoin(SubMenu, Menu.id == SubMenu.menu_id).\
        outerjoin(Dish, SubMenu.id == Dish.submenu_id).\
        group_by(Menu.id).order_by(Menu.id)
    
    menus = []
    submenus_count = get_submenus_count_for_menu_list(session)

    for menu_obj, dishes_count in menus_with_dishes_count:
        setattr(menu_obj, 'dishes_count', dishes_count)
        setattr(menu_obj, 'submenus_count', submenus_count[menu_obj.id])
        menus.append(menu_obj)
    return menus

def get_submenus_count_for_menu_list(session: Session) -> dict:
    """Возвращает количество подменю во всех меню"""
    query_result = session.query(Menu.id, func.count(SubMenu.menu_id)).\
        select_from(Menu).\
        outerjoin(SubMenu, Menu.id == SubMenu.menu_id).\
        group_by(Menu.id).order_by(Menu.id)
    result_dict = {}  # ключ - menu_id, значение - количество подменю
    for key, value in query_result:
        result_dict[key] = value
    return result_dict


def create_menu(session: Session, new_menu: MenuCreate):
    """Создает меню"""
    menu_obj = Menu(**new_menu.model_dump())
    session.add(menu_obj)
    session.commit()
    return menu_obj


def get_menu_by_id(session: Session, menu_id: int):
    "Возвращает меню"
    return session.query(Menu).filter(Menu.id == menu_id).one()


def get_menu_with_counts(session: Session, menu_id: int):
    """Возвращает объект меню с количеством блюд и количеством меню"""
    menu_obj = get_menu_by_id(session, menu_id)

    dishes_count = get_dishes_count_in_menu(session, menu_id)
    submenus_count = get_submenus_count_in_menu(session, menu_id)

    setattr(menu_obj, 'dishes_count', dishes_count)
    setattr(menu_obj, 'submenus_count', submenus_count)
    return menu_obj


def get_submenus_count_in_menu(session: Session, menu_id: int):
    """Возвращает количество подменю в меню"""
    return session.query(func.count(SubMenu.menu_id)).select_from(SubMenu).\
    filter(SubMenu.menu_id == menu_id).scalar()

def update_menu_by_id(session: Session, menu_id: int, item: MenuCreate):
    """Обновляет меню"""
    menu_obj = get_menu_by_id(session, menu_id)
    for key, value in item.model_dump().items():
        setattr(menu_obj, key, value)
    session.commit()
    return get_menu_with_counts(session, menu_id)


def delete_menu_by_id(session: Session, menu_id: int):
    """Удаляет меню"""
    menu_obj = get_menu_by_id(session, menu_id)
    session.delete(menu_obj)
    session.commit()


def get_submenu_list_with_dishes_count(session: Session, menu_id: int):
    """Возвращает список всех подменю с количеством блюд в каждом подменю"""
    submenus_with_dishes_count = session.\
        query(SubMenu, func.count(Dish.id)).\
        select_from(SubMenu).\
        outerjoin(Dish, SubMenu.id == Dish.submenu_id).\
        group_by(SubMenu.id).order_by(SubMenu.id)
    submenus = []
    for submenu_obj, dishes_count in submenus_with_dishes_count:
        setattr(submenu_obj, 'dishes_count', dishes_count)
        submenus.append(submenu_obj)
    return submenus    


def create_submenu(session: Session, new_submenu: SubMenuCreate, 
                   menu_id: int):
    """Создает подменю"""
    submenu_obj = SubMenu(**new_submenu.model_dump())
    submenu_obj.menu_id = menu_id
    session.add(submenu_obj)
    session.commit()
    return submenu_obj


def get_submenu_by_id(session: Session, menu_id: int, submenu_id: int):
    """Возвращает подменю"""
    return session.query(SubMenu).\
        filter(SubMenu.id == submenu_id, SubMenu.menu_id == menu_id).one()


def get_submenu_with_dishes_count(session: Session, 
                                  menu_id: int, submenu_id: int):
    """Возвращает объект подменю с количеством блюд"""
    submenu_obj = get_submenu_by_id(session, menu_id, submenu_id)
    dishes_count = get_count_dishes_in_submenu(session, submenu_id)
    setattr(submenu_obj, 'dishes_count', dishes_count)
    return submenu_obj

def update_submenu_by_id(session: Session, menu_id: int, 
                         submenu_id: int, item: SubMenuCreate):
    """Обновляет подменю"""
    submenu_obj = get_submenu_by_id(session, menu_id, submenu_id)
    for key, value in item.model_dump().items():
        setattr(submenu_obj, key, value)
    session.commit()
    return get_submenu_with_dishes_count(session, menu_id, submenu_id)


def delete_submenu_by_id(session: Session, menu_id: int, submenu_id: int):
    """Удаляет подменю"""
    submenu_obj = get_submenu_by_id(session, menu_id, submenu_id)
    session.delete(submenu_obj)
    session.commit()


def get_dish_list(session: Session, menu_id: int, submenu_id: int):
    """Возвращает список блюд из подменю"""
    return session.query(Dish).\
        join(SubMenu, Dish.submenu_id == submenu_id).\
        join(Menu, SubMenu.menu_id == menu_id).all()


def create_dish(session: Session, new_dish: DishCreate, 
                submenu_id: int):
    """Создает блюдо"""
    dish_obj = Dish(**new_dish.model_dump())
    dish_obj.submenu_id = submenu_id
    session.add(dish_obj)
    session.commit()
    return dish_obj


def get_dish_by_id(session: Session, menu_id: int, 
                   submenu_id: int, dish_id: int):
    """Возвращает блюдо"""
    return session.query(Dish).\
        join(SubMenu, Dish.submenu_id == submenu_id).\
        join(Menu, SubMenu.menu_id == menu_id).\
        filter(Dish.id == dish_id).one()


def update_dish_by_id(session: Session, menu_id: int,
                      submenu_id: int, dish_id: int, item: DishCreate):
    """Обновляет блюдо"""
    dish_obj = get_dish_by_id(session, menu_id, submenu_id, dish_id)
    for key, value in item.model_dump().items():
        setattr(dish_obj, key, value)
    session.commit()
    return dish_obj


def delete_dish_by_id(session: Session, menu_id: int, 
                      submenu_id: int, dish_id: int):
    """Удаляет блюдо"""
    dish_obj = get_dish_by_id(session, menu_id, submenu_id, dish_id)
    session.delete(dish_obj)
    session.commit()


def get_count_dishes_in_submenu(session: Session, submenu_id: int):
    """Возвращает количество блюд в подменю"""
    return session.query(Dish).\
        filter(Dish.submenu_id == submenu_id).count()


def get_dishes_count_in_menu(session: Session, menu_id: int):
    """Возвращает количество блюд в меню"""
    return session.query(func.count(Dish.id)).\
        select_from(Menu).\
        outerjoin(SubMenu, Menu.id == SubMenu.menu_id).\
        outerjoin(Dish, SubMenu.id == Dish.submenu_id).\
        filter(Menu.id == menu_id).scalar()