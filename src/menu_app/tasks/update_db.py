from sqlalchemy import create_engine, delete, insert, select, update
from sqlalchemy.orm import Session, sessionmaker

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from menu_app.tasks.parse_excel import ExcelBackend
from models.models import Base, Dish, Menu, SubMenu

DATABASE_URL =\
    f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DATABASE_URL)
SessionClass = sessionmaker(engine)


def update_db_from_excel() -> None:
    """Обновляет базу данных, используя excel-файл"""
    excel = ExcelBackend()

    menus_from_excel: list[dict] = excel.get_menus()
    submenus_from_excel: list[dict] = excel.get_submenus()
    dishes_from_excel: list[dict] = excel.get_dishes()

    menu_id_list = get_id_list_from_excel(menus_from_excel)
    submenu_id_list = get_id_list_from_excel(submenus_from_excel)
    dish_id_list = get_id_list_from_excel(dishes_from_excel)
    with SessionClass() as session:
        menus_for_create, menus_for_update =\
            get_objects_for_create_and_update(
                menus_from_excel,
                Menu,
                session
            )
        submenus_for_create, submenus_for_update =\
            get_objects_for_create_and_update(
                submenus_from_excel,
                SubMenu,
                session
            )
        dishes_for_create, dishes_for_update =\
            get_objects_for_create_and_update(
                dishes_from_excel,
                Dish,
                session
            )
        session.execute(
            delete(Dish).
            where(~Dish.id.in_(dish_id_list))
        )
        session.execute(
            delete(SubMenu).
            where(~SubMenu.id.in_(submenu_id_list))
        )
        session.execute(
            delete(Menu).
            where(~Menu.id.in_(menu_id_list))
        )
        if menus_for_create:
            session.execute(
                insert(Menu),
                menus_for_create,
            )
        if submenus_for_create:
            session.execute(
                insert(SubMenu),
                submenus_for_create
            )
        if dishes_for_create:
            session.execute(
                insert(Dish),
                dishes_for_create
            )
        if menus_for_update:
            session.execute(
                update(Menu),
                menus_for_update
            )
        if submenus_for_update:
            session.execute(
                update(SubMenu),
                submenus_for_update
            )
        if dishes_for_update:
            session.execute(
                update(Dish),
                dishes_for_update
            )
        session.commit()


def get_id_list_from_excel(objects_from_excel: list[dict]) -> list[int]:
    """Возвращает список id сущностей, которые получены из excel"""
    id_list = [obj['id'] for obj in objects_from_excel]
    return id_list


def get_id_list_from_db(model: Base, session: Session) -> list[int]:
    """Возвращает список id сущностей, которые получены из базы данных"""
    id_list = session.execute(select(model.id))
    return [_tuple[0] for _tuple in id_list.all()]


def get_objects_for_create_and_update(
    list_from_excel: list[dict],
    model: Base,
    session: Session,
) -> list[list]:
    """
    Возвращает два списка - список объектов на добавление
    и список объектов на обновление
    """
    for_create = []
    for_update = []

    id_list = get_id_list_from_db(model, session)
    for obj in list_from_excel:
        if obj['id'] in id_list:
            for_update.append(obj)
        else:
            for_create.append(obj)
    return [for_create, for_update]
