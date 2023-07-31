from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm.exc import NoResultFound

from database import get_session
from . import crud
from .schemas import (
    MenuCreate, 
    MenuGet,
    SubMenuCreate, 
    SubMenuGet, 
    DishCreate,
    DishGet,
)


router = APIRouter(
    prefix='/menus',
    tags=['Menu']
)


@router.get('/', response_model=list[MenuGet])
def menu_list(session=Depends(get_session)):
    return crud.get_menu_list_with_counts(session)


@router.post('/', status_code=status.HTTP_201_CREATED, 
             response_model=MenuGet)
def menu_create(new_menu: MenuCreate, session=Depends(get_session)):
    try:
        menu_obj = crud.create_menu(session, new_menu)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return menu_obj


@router.get('/{menu_id}', response_model=MenuGet)
def menu_detail(menu_id: int, session=Depends(get_session)):
    try:
        menu_obj = crud.get_menu_with_counts(session, menu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found'
        )
    return menu_obj


@router.patch('/{menu_id}', response_model=MenuGet)
def menu_patch(menu: MenuCreate, menu_id: int, 
               session=Depends(get_session)):
    try:
        menu_obj = crud.update_menu_by_id(session, menu_id, menu)
    except (IntegrityError, NoResultFound):
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return menu_obj


@router.delete('/{menu_id}')
def menu_delete(menu_id: int, session=Depends(get_session)):
    try:
        crud.delete_menu_by_id(session, menu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found'
        )
    return {'detail': 'success'}


@router.get('/{menu_id}/submenus', response_model=list[SubMenuGet])
def submenu_list(menu_id: int, session=Depends(get_session)):
    return crud.get_submenu_list_with_dishes_count(session, menu_id)
    

@router.post('/{menu_id}/submenus', status_code=status.HTTP_201_CREATED,
             response_model=SubMenuGet)
def submenu_create(menu_id: int, new_submenu: SubMenuCreate, 
                   session=Depends(get_session)):
    try:
        submenu_obj = crud.create_submenu(session, new_submenu, menu_id)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return submenu_obj


@router.get('/{menu_id}/submenus/{submenu_id}', response_model=SubMenuGet)
def submenu_detail(menu_id: int, submenu_id: int, 
                   session=Depends(get_session)):
    try:
        submenu_obj = crud.\
        get_submenu_with_dishes_count(session, menu_id, submenu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='submenu not found'
        )
    return submenu_obj


@router.patch('/{menu_id}/submenus/{submenu_id}', response_model=SubMenuGet)
def submenu_patch(submenu: SubMenuCreate, menu_id: int, 
                  submenu_id: int, session=Depends(get_session)):
    try:
        submenu_obj = crud.update_submenu_by_id(session, menu_id,
                                             submenu_id, submenu)
    except (IntegrityError, NoResultFound):
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return submenu_obj


@router.delete('/{menu_id}/submenus/{submenu_id}')
def submenu_delete(menu_id: int, submenu_id: int, 
                  session=Depends(get_session)):
    try:
        crud.delete_submenu_by_id(session, menu_id, submenu_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='SubMenu not found'
        )
    return {'detail': 'success'}


@router.get('/{menu_id}/submenus/{submenu_id}/dishes',
            response_model=list[DishGet])
def dish_list(menu_id: int, submenu_id: int, session=Depends(get_session)):
    return crud.get_dish_list(session, menu_id, submenu_id)
    

@router.post('/{menu_id}/submenus/{submenu_id}/dishes', 
             status_code=status.HTTP_201_CREATED, response_model=DishGet)
def dish_create(menu_id: int, submenu_id: int, 
                new_dish: DishCreate, session=Depends(get_session)):
    try:
        dish_obj = crud.create_dish(session, new_dish, submenu_id)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return dish_obj


@router.get('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', 
            response_model=DishGet)
def dish_detail(menu_id: int, submenu_id: int, dish_id: int, 
                session=Depends(get_session)):
    try:
        dish_obj = crud.get_dish_by_id(session, menu_id, 
                                       submenu_id, dish_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )
    return dish_obj


@router.patch('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
              response_model=DishGet)
def dish_patch(dish: DishCreate, 
               menu_id: int, submenu_id: int, dish_id: int, 
               session=Depends(get_session)):
    try:
        dish_obj = crud.update_dish_by_id(session, menu_id, submenu_id,
                                          dish_id, dish)
    except (IntegrityError, NoResultFound):
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    return dish_obj


@router.delete('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
def dish_delete(menu_id: int, submenu_id: int, dish_id: int,
                session=Depends(get_session)):
    try:
        crud.delete_dish_by_id(session, menu_id, submenu_id, dish_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )
    return {'detail': 'success'}