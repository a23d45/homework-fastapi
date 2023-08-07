from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .schemas import DishCreate, DishGet, MenuCreate, MenuGet, SubMenuCreate, SubMenuGet
from .services.dish_service import DishService
from .services.menu_service import MenuService
from .services.submenu_service import SubMenuService

menu_router: APIRouter = APIRouter(
    prefix='/menus',
    tags=['Menu']
)


@menu_router.get('/', response_model=list[MenuGet])
def menu_list(menu_service: MenuService = Depends(MenuService)):
    return menu_service.get_menu_list_with_counts()


@menu_router.post('/', status_code=status.HTTP_201_CREATED,
                  response_model=MenuGet)
def menu_create(
    new_menu: MenuCreate,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        menu_obj = menu_service.create_menu(new_menu)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return menu_obj


@menu_router.get('/{menu_id}', response_model=MenuGet)
def menu_detail(
    menu_id: int,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        menu_obj = menu_service.get_menu_with_counts(menu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found'
        )
    return menu_obj


@menu_router.patch('/{menu_id}', response_model=MenuGet)
def menu_patch(
    menu: MenuCreate,
    menu_id: int,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        menu_obj = menu_service.update_menu_by_id(menu_id, menu)
    except (IntegrityError, NoResultFound):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return menu_obj


@menu_router.delete('/{menu_id}')
def menu_delete(
    menu_id: int,
    menu_service: MenuService = Depends(MenuService)
):
    try:
        menu_service.delete_menu_by_id(menu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found'
        )
    return {'detail': 'success'}


@menu_router.get('/{menu_id}/submenus', response_model=list[SubMenuGet])
def submenu_list(
    menu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    return submenu_service.\
        get_submenu_list_with_dishes_count(menu_id)


@menu_router.post('/{menu_id}/submenus', status_code=status.HTTP_201_CREATED,
                  response_model=SubMenuGet)
def submenu_create(
    menu_id: int,
    new_submenu: SubMenuCreate,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        submenu_obj = submenu_service.\
            create_submenu(new_submenu, menu_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return submenu_obj


@menu_router.get('/{menu_id}/submenus/{submenu_id}', response_model=SubMenuGet)
def submenu_detail(
    menu_id: int,
    submenu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        submenu_obj = submenu_service.\
            get_submenu_with_dishes_count(menu_id, submenu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='submenu not found'
        )
    return submenu_obj


@menu_router.patch('/{menu_id}/submenus/{submenu_id}', response_model=SubMenuGet)
def submenu_patch(
    submenu: SubMenuCreate,
    menu_id: int,
    submenu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        submenu_obj = submenu_service.\
            update_submenu_by_id(menu_id, submenu_id, submenu)
    except (IntegrityError, NoResultFound):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return submenu_obj


@menu_router.delete('/{menu_id}/submenus/{submenu_id}')
def submenu_delete(
    menu_id: int,
    submenu_id: int,
    submenu_service: SubMenuService = Depends(SubMenuService)
):
    try:
        submenu_service.\
            delete_submenu_by_id(menu_id, submenu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='SubMenu not found'
        )
    return {'detail': 'success'}


@menu_router.get('/{menu_id}/submenus/{submenu_id}/dishes',
                 response_model=list[DishGet])
def dish_list(
    menu_id: int,
    submenu_id: int,
    dish_service: DishService = Depends(DishService)
):
    return dish_service\
        .get_dish_list(menu_id, submenu_id)


@menu_router.post('/{menu_id}/submenus/{submenu_id}/dishes',
                  status_code=status.HTTP_201_CREATED, response_model=DishGet)
def dish_create(
    menu_id: int,
    submenu_id: int,
    new_dish: DishCreate,
    dish_service: DishService = Depends(DishService)
):
    try:
        dish_obj = dish_service.\
            create_dish(new_dish, submenu_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return dish_obj


@menu_router.get('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
                 response_model=DishGet)
def dish_detail(
    menu_id: int,
    submenu_id: int,
    dish_id: int,
    dish_service: DishService = Depends(DishService)
):
    try:
        dish_obj = dish_service.\
            get_dish_by_id(menu_id, submenu_id, dish_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )
    return dish_obj


@menu_router.patch('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
                   response_model=DishGet)
def dish_patch(
    dish: DishCreate,
    menu_id: int,
    submenu_id: int,
    dish_id: int,
    dish_service: DishService = Depends(DishService)
):
    try:
        dish_obj = dish_service.\
            update_dish_by_id(menu_id, submenu_id, dish_id, dish)
    except (IntegrityError, NoResultFound):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return dish_obj


@menu_router.delete('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def dish_delete(
    menu_id: int,
    submenu_id: int,
    dish_id: int,
    dish_service: DishService = Depends(DishService)
):
    try:
        dish_service.delete_dish_by_id(menu_id, submenu_id, dish_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )
    return {'detail': 'success'}
