from sqlalchemy import delete, insert, select, update

from database import AsyncSession
from menu_app.tasks.parse_excel import ExcelBackend
from models.models import Base, Dish, Menu, SubMenu


async def update_db_from_excel() -> None:
    """Обновляет базу данных, используя excel-файл"""
    excel = ExcelBackend()

    menus_from_excel = excel.get_menus()
    submenus_from_excel = excel.get_submenus()
    dishes_from_excel = excel.get_dishes()

    menu_id_list = get_id_list_from_excel(menus_from_excel)
    submenu_id_list = get_id_list_from_excel(submenus_from_excel)
    dish_id_list = get_id_list_from_excel(dishes_from_excel)

    async with AsyncSession() as session:
        menus_for_create, menus_for_update =\
            await get_objects_for_create_and_update(
                menus_from_excel,
                Menu,
                session
            )
        submenus_for_create, submenus_for_update =\
            await get_objects_for_create_and_update(
                submenus_from_excel,
                SubMenu,
                session
            )
        dishes_for_create, dishes_for_update =\
            await get_objects_for_create_and_update(
                dishes_from_excel,
                Dish,
                session
            )
        await session.execute(
            delete(Dish).
            where(~Dish.id.in_(dish_id_list))
        )
        await session.execute(
            delete(SubMenu).
            where(~SubMenu.id.in_(submenu_id_list))
        )
        await session.execute(
            delete(Menu).
            where(~Menu.id.in_(menu_id_list))
        )
        if menus_for_create:
            await session.execute(
                insert(Menu),
                menus_for_create,
            )
        if submenus_for_create:
            await session.execute(
                insert(SubMenu),
                submenus_for_create
            )
        if dishes_for_create:
            await session.execute(
                insert(Dish),
                dishes_for_create
            )
        if menus_for_update:
            await session.execute(
                update(Menu),
                menus_for_update
            )
        if submenus_for_update:
            await session.execute(
                update(SubMenu),
                submenus_for_update
            )
        if dishes_for_update:
            await session.execute(
                update(Dish),
                dishes_for_update
            )
        await session.commit()


def get_id_list_from_excel(objects_from_excel: list[dict]) -> list[int]:
    """Возвращает список id сущностей, которые получены из excel"""
    id_list = [obj['id'] for obj in objects_from_excel]
    return id_list


async def get_id_list_from_db(model: Base, session: AsyncSession) -> list[int]:
    """Возвращает список id сущностей, которые получены из базы данных"""
    id_list = await session.execute(select(model.id))
    return [_tuple[0] for _tuple in id_list.all()]


async def get_objects_for_create_and_update(
    list_from_excel: list[dict],
    model: Base,
    session: AsyncSession,
) -> tuple[list[dict]]:
    """
    Возвращает два списка - список объектов на добавление
    и список объектов на обновление
    """
    for_create = []
    for_update = []

    id_list = await get_id_list_from_db(model, session)
    for obj in list_from_excel:
        if obj['id'] in id_list:
            for_update.append(obj)
        else:
            for_create.append(obj)
    return (for_create, for_update)
