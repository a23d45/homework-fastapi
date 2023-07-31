import json


prefix = 'api/v1'


def test_get_menu_empty_list(client):
    response = client.get(f'{prefix}/menus')
    assert response.status_code == 200
    assert response.json() == []


def test_create_menu(client):
    data = {
        'title': 'Menu 1',
        'description': 'Some description',
    }
    response = client.post(
        f'{prefix}/menus', 
        content=json.dumps(data)
    )
    response_data = response.json()
    assert response.status_code == 201
    assert isinstance(response_data['id'], str) 
    assert response_data['title'] == data['title']
    assert response_data['description'] == data['description']


def test_get_submenu_empty_list(client, current_menu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}/submenus'
    )
    assert response.status_code == 200
    assert response.json() == []


def test_create_submenu(client, current_menu):
    data = {
        'title': 'Submenu 1',
        'description': 'Some description',
    }
    response = client.post(
        f'{prefix}/menus/{current_menu.id}/submenus', 
        content=json.dumps(data)
    )
    response_data = response.json()
    assert response.status_code == 201
    assert isinstance(response_data['id'], str) 
    assert response_data['title'] == data['title']
    assert response_data['description'] == data['description']


def test_get_dish_empty_list(client, current_menu, current_submenu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}' + \
            f'/submenus/{current_submenu.id}/dishes'
    )
    assert response.status_code == 200
    assert response.json() == []


def test_create_dish(client, current_menu, current_submenu):
    data = {
        'title': 'Dish 1',
        'description': 'Some description',
        'price': '14.15'
    }
    response = client.post(
        f'{prefix}/menus/{current_menu.id}' + \
            f'/submenus/{current_submenu.id}/dishes',
        content=json.dumps(data)
    )
    response_data = response.json()
    assert response.status_code == 201
    assert isinstance(response_data['id'], str) 
    assert response_data['title'] == data['title']
    assert response_data['description'] == data['description']
    assert response_data['price'] == data['price']


def test_get_menu_list(client):
    response = client.get(f'{prefix}/menus')
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == 1


def test_get_menu_detail(client, current_menu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_menu.id) == response_data['id']
    assert current_menu.title == response_data['title']
    assert current_menu.description == response_data['description']


def test_update_menu(client, current_menu):
    data = {
        'title': 'Updated menu',
        'description': 'Updated description'
    }
    response = client.patch(
        f'{prefix}/menus/{current_menu.id}',
        content=json.dumps(data)
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_menu.id) == response_data['id']
    assert data['title'] == response_data['title']
    assert data['description'] == response_data['description']


def test_get_submenu_list(client, current_menu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}/submenus'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == 1


def test_get_submenu_detail(client, current_menu, current_submenu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}' + \
            f'/submenus/{current_submenu.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_submenu.id) == response_data['id']
    assert current_submenu.title == response_data['title']
    assert current_submenu.description == response_data['description']


def test_update_submenu(client, current_menu, current_submenu):
    data = {
        'title': 'Updated submenu',
        'description': 'Updated description'
    }
    response = client.patch(
        f'{prefix}/menus/{current_menu.id}'+ \
                f'/submenus/{current_submenu.id}',
        content=json.dumps(data)
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_submenu.id) == response_data['id']
    assert data['title'] == response_data['title']
    assert data['description'] == response_data['description']


def test_get_dish_list(client, current_menu, current_submenu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}' + \
                f'/submenus/{current_submenu.id}/dishes'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == 1


def test_get_dish_detail(client, current_menu,
                         current_submenu, current_dish):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}' + \
                f'/submenus/{current_submenu.id}' + \
                f'/dishes/{current_dish.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_dish.id) == response_data['id']
    assert current_dish.title == response_data['title']
    assert current_dish.description == response_data['description']
    assert current_dish.price == response_data['price']


def test_update_dish(client, current_menu, 
                     current_submenu, current_dish):
    data = {
        'title': 'Updated dish',
        'description': 'Updated description',
        'price': '20.10'
    }
    response = client.patch(
        f'{prefix}/menus/{current_menu.id}'+ \
                f'/submenus/{current_submenu.id}' + \
                f'/dishes/{current_dish.id}',
        content=json.dumps(data)
    )
    response_data = response.json()
    assert response.status_code == 200
    assert str(current_submenu.id) == response_data['id']
    assert data['title'] == response_data['title']
    assert data['description'] == response_data['description']
    assert data['price'] == response_data['price']



def test_incorrect_price_update_dish(client, current_menu, 
                                     current_submenu, current_dish):
    data = {
        'title': 'Updated dish',
        'description': 'Updated description',
        'price': 'hello world'
    }
    response = client.patch(
        f'{prefix}/menus/{current_menu.id}'+ \
                f'/submenus/{current_submenu.id}' + \
                f'/dishes/{current_dish.id}',
        content=json.dumps(data)
    )
    assert response.status_code == 422
    

def test_delete_dish(client, current_menu, 
                     current_submenu, current_dish):
    response = client.delete(
        f'{prefix}/menus/{current_menu.id}' + \
                f'/submenus/{current_submenu.id}' + \
                f'/dishes/{current_dish.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['detail'] == 'success'


def test_delete_submenu(client, current_menu, current_submenu):
    response = client.delete(
        f'{prefix}/menus/{current_menu.id}' + \
                f'/submenus/{current_submenu.id}'
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['detail'] == 'success'


def test_delete_menu(client, current_menu):
    response = client.delete(
        f'{prefix}/menus/{current_menu.id}',
    )
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['detail'] == 'success'


def test_failed_get_menu_detail(client, current_menu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}'
    )
    assert response.status_code == 404


def test_failed_update_menu(client, current_menu):
    data = {
        'title': 'Failed title',
        'description': 'Failed description'
    }
    response = client.patch(
        f'{prefix}/menus/{current_menu.id}',
        content=json.dumps(data)
    )
    assert response.status_code == 409


def test_failed_get_menu_detail(client, current_menu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}'
    )
    assert response.status_code == 404


def test_failed_update_submenu(client, current_menu, current_submenu):
    data = {
        'title': 'Failed title',
        'description': 'Failed description'
    }
    response = client.patch(
        f'{prefix}/menus/{current_menu.id}'+ \
                f'/submenus/{current_submenu.id}',
        content=json.dumps(data)
    )
    assert response.status_code == 409


def test_failed_get_submenu_detail(client, current_menu, current_submenu):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}'+ \
                f'/submenus/{current_submenu.id}'
    )
    assert response.status_code == 404


def test_failed_update_dish(client, current_menu, 
                             current_submenu, current_dish):
    data = {
        'title': 'Failed title',
        'description': 'Failed description',
        'price': '9.92'
    }
    response = client.patch(
        f'{prefix}/menus/{current_menu.id}' + \
                f'/submenus/{current_submenu.id}' + \
                f'/dishes/{current_dish.id}',
        content=json.dumps(data)
    )            
    assert response.status_code == 409




def test_failed_get_dish_detail(client, current_menu, 
                                current_submenu, current_dish):
    response = client.get(
        f'{prefix}/menus/{current_menu.id}' + \
                f'/submenus/{current_submenu.id}' + \
                f'/dishes/{current_dish.id}'
    )
    assert response.status_code == 404

