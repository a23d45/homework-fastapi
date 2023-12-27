from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.exc import NoResultFound

from menu_app import schemas
from menu_app.services.dish_service import DishService
from menu_app.services.menu_service import MenuService
from menu_app.services.submenu_service import SubMenuService


menu_router: APIRouter = APIRouter(
    prefix='/menus',
    tags=['Menu']
)


@menu_router.get('', response_model=list[schemas.MenuGet])
async def menu_list(menu_service: MenuService = Depends(MenuService)):
    return await menu_service.get_menu_list_with_counts()


@menu_router.get(
    '/all',
    response_model=list[schemas.MenuWithNestedSubMenus]
)
async def get_all(menu_service: MenuService = Depends(MenuService)):
    return await menu_service.get_all_list()


@menu_router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MenuGet
)
async def menu_create(
    new_menu: schemas.MenuCreate,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        menu_obj = await menu_service.create_menu(new_menu)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return menu_obj


@menu_router.get('/{menu_id}', response_model=schemas.MenuGet)
async def menu_detail(
    menu_id: int,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        menu_obj = await menu_service.get_menu_with_counts(menu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found'
        )
    return menu_obj


@menu_router.patch('/{menu_id}', response_model=schemas.MenuGet)
async def menu_patch(
    menu: schemas.MenuCreate,
    menu_id: int,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        menu_obj = await menu_service.update_menu_by_id(menu_id, menu)
    except (ValueError, NoResultFound):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return menu_obj


@menu_router.delete('/{menu_id}')
async def menu_delete(
    menu_id: int,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        await menu_service.delete_menu_by_id(menu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found'
        )
    return {'detail': 'success'}


@menu_router.get(
    '/{menu_id}/submenus',
    response_model=list[schemas.SubMenuGet]
)
async def submenu_list(
    menu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    return await submenu_service.\
        get_submenu_list_with_dishes_count(menu_id)


@menu_router.post(
    '/{menu_id}/submenus',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.SubMenuGet
)
async def submenu_create(
    menu_id: int,
    new_submenu: schemas.SubMenuCreate,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        submenu_obj = await submenu_service.\
            create_submenu(new_submenu, menu_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return submenu_obj


@menu_router.get(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=schemas.SubMenuGet
)
async def submenu_detail(
    menu_id: int,
    submenu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        submenu_obj = await submenu_service.\
            get_submenu_with_dishes_count(menu_id, submenu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='submenu not found'
        )
    return submenu_obj


@menu_router.patch(
    '/{menu_id}/submenus/{submenu_id}',
    response_model=schemas.SubMenuGet
)
async def submenu_patch(
    submenu: schemas.SubMenuCreate,
    menu_id: int,
    submenu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        submenu_obj = await submenu_service.\
            update_submenu_by_id(menu_id, submenu_id, submenu)
    except (ValueError, NoResultFound):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return submenu_obj


@menu_router.delete('/{menu_id}/submenus/{submenu_id}')
async def submenu_delete(
    menu_id: int,
    submenu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        await submenu_service.\
            delete_submenu_by_id(menu_id, submenu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='SubMenu not found'
        )
    return {'detail': 'success'}


@menu_router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    response_model=list[schemas.DishGet]
)
async def dish_list(
    menu_id: int,
    submenu_id: int,
    dish_service: DishService = Depends(DishService)
):
    result = await dish_service.\
        get_dish_list(menu_id, submenu_id)
    return result


@menu_router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.DishGet
)
async def dish_create(
    menu_id: int,
    submenu_id: int,
    new_dish: schemas.DishCreate,
    dish_service: DishService = Depends(DishService)
):
    try:
        dish_obj = await dish_service.\
            create_dish(new_dish, menu_id, submenu_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return dish_obj


@menu_router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=schemas.DishGet
)
async def dish_detail(
    menu_id: int,
    submenu_id: int,
    dish_id: int,
    dish_service: DishService = Depends(DishService)
):
    try:
        dish_obj = await dish_service.\
            get_dish_by_id(menu_id, submenu_id, dish_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )
    return dish_obj


@menu_router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    response_model=schemas.DishGet
)
async def dish_patch(
    dish: schemas.DishCreate,
    menu_id: int,
    submenu_id: int,
    dish_id: int,
    dish_service: DishService = Depends(DishService)
):
    try:
        dish_obj = await dish_service.\
            update_dish_by_id(menu_id, submenu_id, dish_id, dish)
    except (ValueError, NoResultFound):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return dish_obj


@menu_router.delete('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def dish_delete(
    menu_id: int,
    submenu_id: int,
    dish_id: int,
    dish_service: DishService = Depends(DishService)
):
    try:
        await dish_service.delete_dish_by_id(menu_id, submenu_id, dish_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )
    return {'detail': 'success'}
