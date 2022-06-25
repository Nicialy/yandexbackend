from typing import Type
from uuid import UUID
from asyncpg import Record
from app.models import BaseModel, ShopUnit, ShopUnitStatisticResponse, ShopUnitStatisticUnit, ShopUnitType
from collections import defaultdict


def format_nodes(raw_records: list[Record]) -> BaseModel:
    items = format_dict(format_records(raw_records))
    return items


def format_sales(raw_records: list[Record], model: Type[ShopUnitStatisticUnit]) -> ShopUnitStatisticResponse:
    if not raw_records:
        return ShopUnitStatisticResponse(items=[])
    return ShopUnitStatisticResponse(
        items=list(
            map(
                lambda raw_record: model(
                    id=raw_record["id"],
                    name=raw_record["name_item"],
                    type=raw_record["shop_type"],
                    date=raw_record["date_update"].replace(tzinfo=None).isoformat(timespec="milliseconds") + "Z",
                    price=raw_record["price"],
                    parentId=raw_record["parent_id"],
                ),
                raw_records,
            )
        )
    )


def format_records(raw_records: Record) -> defaultdict(list):
    data_dict = defaultdict(list)
    for raw_record in raw_records:
        data_dict[raw_record["parent_id"]].append(
            {
                "id": raw_record["id"],
                "name": raw_record["name_item"],
                "type": raw_record["shop_type"],
                "date": raw_record["date_update"].replace(tzinfo=None).isoformat(timespec="milliseconds") + "Z",
                "price": raw_record["price"],
                "parentId": raw_record["parent_id"],
            }
        )
    return data_dict


def format_dict(data_dict: defaultdict(list), parent_id: UUID = None, i: int = 0, shop_type: ShopUnitType = None):
    if i == 0:
        key = list(data_dict.keys())[0]
        data = data_dict[key][0]
        return ShopUnit(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            date=data["date"],
            price=data["price"],
            parentId=data["parentId"],
            children=format_dict(data_dict, data["id"], i + 1, data["type"]),
        )
    else:
        if not data_dict[parent_id] and shop_type == ShopUnitType.OFFER.value:
            return None
    return [
        ShopUnit(
            id=item["id"],
            name=item["name"],
            type=item["type"],
            date=item["date"],
            price=item["price"],
            parentId=item["parentId"],
            children=format_dict(data_dict, item["id"], i + 1, item["type"]),
        )
        for item in data_dict[parent_id]
    ]
