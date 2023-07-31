from typing import Union
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, field_validator


class AbstractEntity(BaseModel):
    title: str
    description: str


class IdMixin(BaseModel):
    id: Union[int, str]

    @field_validator('id')
    def int_to_str(cls, value):
        return str(value)
    

class MenuCreate(AbstractEntity):
    pass


class SubMenuCreate(AbstractEntity):
    pass


class DishCreate(AbstractEntity):
    price: Union[str, Decimal]

    @field_validator('price')
    def validate_price(cls, value):
        try:
            decimal_price = Decimal(value).quantize(Decimal('0.01'))
        except InvalidOperation:
            raise ValueError("price is invalid")
        return decimal_price


class MenuGet(MenuCreate, IdMixin):
    submenus_count: int = 0
    dishes_count: int = 0


class SubMenuGet(SubMenuCreate, IdMixin):
    dishes_count: int = 0 


class DishGet(DishCreate, IdMixin):
    pass

