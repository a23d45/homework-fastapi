import json

from httpx import AsyncClient

prefix = 'api/v1'


async def test_get_menu_empty_list(client: AsyncClient):
    response = await client.get(f'{prefix}/menus')
    assert response.status_code == 200
    assert response.json() == []


async def test_create_menu(client: AsyncClient):
    data = {
        'title': 'Menu 1',
        'description': 'Some description',
    }
    response = await client.post(
        f'{prefix}/menus',
        json=data,
    )
    response_data = response.json()
    assert response.status_code == 201
    assert isinstance(response_data['id'], str)
    assert response_data['title'] == data['title']
    assert response_data['description'] == data['description']


async def test_get_submenu_empty_list(client: AsyncClient, current_menu):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}/submenus'
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_create_submenu(client: AsyncClient, current_menu):
    data = {
        'title': 'SubMenu 1',
        'description': 'Some description',
    }
    response = await client.post(
        f'{prefix}/menus/{current_menu.id}/submenus',
        json=data
    )
    response_data = response.json()
    assert response.status_code == 201
    assert isinstance(response_data['id'], str)
    assert response_data['title'] == data['title']
    assert response_data['description'] == data['description']


async def test_get_dish_empty_list(
    client: AsyncClient,
    current_menu,
    current_submenu
):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}/dishes'
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_create_dish(
    client: AsyncClient,
    current_menu,
    current_submenu
):
    data = {
        'title': 'Dish 1',
        'description': 'Some description',
        'price': '14.15'
    }
    response = await client.post(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}/dishes',
        json=data
    )
    response_data = response.json()
    assert response.status_code == 201
    assert isinstance(response_data['id'], str)
    assert response_data['title'] == data['title']
    assert response_data['description'] == data['description']
    assert response_data['price'] == data['price']


async def test_get_all_list(client: AsyncClient):
    response = await client.get(f'{prefix}/menus/all')
    response_data = response.json()

    assert response.status_code == 200
    assert isinstance(response_data, list)

    menu_obj = response_data[0]
    assert menu_obj['title'] == 'Menu 1'
    assert isinstance(menu_obj['submenus'], list)

    submenu_obj = menu_obj['submenus'][0]
    assert submenu_obj['title'] == 'SubMenu 1'
    assert isinstance(submenu_obj['dishes'], list)

    dish_obj = submenu_obj['dishes'][0]
    assert dish_obj['title'] == 'Dish 1'


async def test_get_menu_list(client: AsyncClient):
    response = await client.get(f'{prefix}/menus')
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == 1


async def test_get_menu_detail(client: AsyncClient, current_menu):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_menu.id) == response_data['id']
    assert current_menu.title == response_data['title']
    assert current_menu.description == response_data['description']


async def test_update_menu(client: AsyncClient, current_menu):
    data = {
        'title': 'Updated menu',
        'description': 'Updated description'
    }
    response = await client.patch(
        f'{prefix}/menus/{current_menu.id}',
        json=data
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_menu.id) == response_data['id']
    assert data['title'] == response_data['title']
    assert data['description'] == response_data['description']


async def test_get_submenu_list(client: AsyncClient, current_menu):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}/submenus'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == 1


async def test_get_submenu_detail(
    client: AsyncClient,
    current_menu,
    current_submenu
):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_submenu.id) == response_data['id']
    assert current_submenu.title == response_data['title']
    assert current_submenu.description == response_data['description']


async def test_update_submenu(
    client: AsyncClient,
    current_menu,
    current_submenu
):
    data = {
        'title': 'Updated submenu',
        'description': 'Updated description'
    }
    response = await client.patch(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}',
        json=data
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_submenu.id) == response_data['id']
    assert data['title'] == response_data['title']
    assert data['description'] == response_data['description']


async def test_get_dish_list(
    client: AsyncClient,
    current_menu,
    current_submenu
):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}/dishes'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == 1


async def test_get_dish_detail(
    client: AsyncClient,
    current_menu,
    current_submenu,
    current_dish
):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
        + f'/dishes/{current_dish.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_dish.id) == response_data['id']
    assert current_dish.title == response_data['title']
    assert current_dish.description == response_data['description']
    assert current_dish.price == response_data['price']


async def test_update_dish(
    client: AsyncClient,
    current_menu,
    current_submenu,
    current_dish
):
    data = {
        'title': 'Updated dish',
        'description': 'Updated description',
        'price': '20.10'
    }
    response = await client.patch(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
        + f'/dishes/{current_dish.id}',
        json=data
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_submenu.id) == response_data['id']
    assert data['title'] == response_data['title']
    assert data['description'] == response_data['description']
    assert data['price'] == response_data['price']


async def test_incorrect_price_update_dish(
    client: AsyncClient,
    current_menu,
    current_submenu,
    current_dish
):
    data = {
        'title': 'Updated dish',
        'description': 'Updated description',
        'price': 'hello world'
    }
    response = await client.patch(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
        + f'/dishes/{current_dish.id}',
        json=data
    )
    assert response.status_code == 422


async def test_delete_dish(
    client: AsyncClient,
    current_menu,
    current_submenu,
    current_dish
):
    response = await client.delete(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
        + f'/dishes/{current_dish.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['detail'] == 'success'


async def test_delete_submenu(client: AsyncClient, current_menu, current_submenu):
    response = await client.delete(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['detail'] == 'success'


async def test_delete_menu(client: AsyncClient, current_menu):
    response = await client.delete(
        f'{prefix}/menus/{current_menu.id}',
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['detail'] == 'success'


async def test_failed_get_menu_detail(client: AsyncClient, current_menu):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
    )
    assert response.status_code == 404


async def test_failed_update_menu(client: AsyncClient, current_menu):
    data = {
        'title': 'Failed title',
        'description': 'Failed description'
    }
    response = await client.patch(
        f'{prefix}/menus/{current_menu.id}',
        json=data
    )
    assert response.status_code == 409


async def test_failed_get_menu_detail(client: AsyncClient, current_menu):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
    )
    assert response.status_code == 404


async def test_failed_update_submenu(
    client: AsyncClient,
    current_menu,
    current_submenu
):
    data = {
        'title': 'Failed title',
        'description': 'Failed description'
    }
    response = await client.patch(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}',
        json=data
    )
    assert response.status_code == 409


async def test_failed_get_submenu_detail(
    client: AsyncClient,
    current_menu,
    current_submenu
):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
    )
    assert response.status_code == 404


async def test_failed_update_dish(
    client: AsyncClient,
    current_menu,
    current_submenu,
    current_dish
):
    data = {
        'title': 'Failed title',
        'description': 'Failed description',
        'price': '9.92'
    }
    response = await client.patch(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
        + f'/dishes/{current_dish.id}',
        json=data
    )
    assert response.status_code == 409


async def test_failed_get_dish_detail(
    client: AsyncClient,
    current_menu,
    current_submenu,
    current_dish
):
    response = await client.get(
        f'{prefix}/menus/{current_menu.id}'
        + f'/submenus/{current_submenu.id}'
        + f'/dishes/{current_dish.id}'
    )
    assert response.status_code == 404
