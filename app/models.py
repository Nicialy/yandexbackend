from enum import Enum
from typing import List, Union
from uuid import UUID
from pydantic import BaseModel, Field, ValidationError, root_validator
from datetime import datetime


class ShopUnitType(str, Enum):
    OFFER = "OFFER"
    CATEGORY = "CATEGORY"


class SuccessfulResponse(BaseModel):
    details: str = Field("Вставка или обновление прошли успешно", title="Статус операции")


class ShopUnitImport(BaseModel):
    id: UUID
    name: str
    parentId: Union[UUID, None]= None
    price: Union[int, None] = Field(gt=0,lt=2147483647)# TODO меньше 
    type: ShopUnitType

    @root_validator
    def check_price(cls, values):
        if ShopUnitType.OFFER.value == values["type"] and values.get("price") is None:
            raise ValidationError
        elif ShopUnitType.CATEGORY.value == values["type"] and values.get("price") is not None:
            raise ValidationError
        return values


class ShopUnitImportRequest(BaseModel):
    items: List[ShopUnitImport]
    updateDate: datetime


class ShopUnit(BaseModel):
    id: UUID
    name: str
    type: ShopUnitType
    parentId: UUID = None
    date: Union[str, datetime]
    price: Union[int, None] = Field(gt=0)
    children: List["ShopUnit"] = None


class ShopUnitStatisticUnit(BaseModel):
    id: UUID
    name: str
    type: ShopUnitType
    parentId: UUID = None
    date: Union[str, datetime]
    price: Union[int, None] = Field(gt=0)


class ShopUnitStatisticResponse(BaseModel):
    items: List[ShopUnitStatisticUnit]
