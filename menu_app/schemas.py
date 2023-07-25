from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, validator


class AbstractEntity(BaseModel):
    title: str
    description: str


class IdMixin(BaseModel):
    id: int

    @validator('id')
    def int_to_str(cls, value):
        return str(value)
    

class MenuCreate(AbstractEntity):
    pass


class SubMenuCreate(AbstractEntity):
    pass

class DishCreate(AbstractEntity):
    price: str


class MenuGet(MenuCreate, IdMixin):
    submenus_count: int = 0
    dishes_count: int = 0


class SubMenuGet(SubMenuCreate, IdMixin):
    dishes_count: int = 0 


class DishGet(DishCreate, IdMixin):
    
    @validator('price')
    def round_prive(cls, value):
        return Decimal(value).quantize(Decimal('0.01'))

