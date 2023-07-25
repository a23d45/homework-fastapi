# REST API меню ресторана
Проект реализован в качестве домашнего задания при прохождении интенсива *«Python Y_lab»*. Приложение предоставляет API для работы с меню ресторана: создание, удаление, обновление меню, подменю и блюд.
___
## Технологии:
+ FastAPI
+ SQLAlchemy
+ Pydantic
+ Pytest
+ Redis
+ PostgreSQL
+ Docker
___
## Функционал
+ Асинхронные CRUD операции для меню, подменю и блюд
+ Тестирование API
+ Кеширование, инвалидация кеша
___
## Установка
Для запуска приложения требуется Python и установленный пакетный менеджер pip. Следуйте инструкциям ниже, чтобы установить зависимости и запустить приложение:

**1. Клонируйте репозиторий на свой компьютер:**
```
git clone https://github.com/a23d45/homework-fastapi.git
```

**2. Перейдите в директорию проекта. Создайте виртуальное окружение и активируйте его:**
```
python3 -m venv venv
source venv/bin/activate
```


**3. Установите зависимости:**
```
pip install -r requirements.txt
```


**4. Выполните миграции базы данных:**
```
alembic upgrade head
```


**5. В директории src запустите веб-сервер:**
```
uvicorn main:app --reload
```


**6. Откройте браузер и перейдите по адресу http://localhost:8000/docs, чтобы протестировать API**


**7. Запустите тесты в корневой директории проекта:**
```
pytest -v
```


## Docker
### Запуск проекта
**1. В корневой директории проекта выполните:**
```
docker-compose -f docker-compose.yml up
```


**2. Приложение будет доступно по адресу http://localhost:8000/**

### Тестирование
**1. В корневой директории проекта выполните:**
```
docker-compose -f docker-compose-tests.yml up
```


**2. Результаты тестирования будут доступны в консоли**
