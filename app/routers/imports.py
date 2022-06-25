from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Path, Query, status, Request
from app.models import (
    ShopUnitImportRequest,
    ShopUnit,
    ShopUnitStatisticResponse,
    ShopUnitStatisticUnit,
    SuccessfulResponse,
)
from app.queries.imports import add_items_sql, delete_item_sql, get_nodes_sql, get_sales_sql
from app.utils import format_nodes, format_sales
from app.limiter import limiter

imports_router = APIRouter(tags=["Imports"])


@imports_router.post("/imports", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
@limiter.limit(limit_value="1000/minute")
async def add_items(request: Request, items: ShopUnitImportRequest):
    await add_items_sql(items)
    return SuccessfulResponse()


@imports_router.delete("/delete/{id}", response_model=SuccessfulResponse, status_code=status.HTTP_200_OK)
@limiter.limit(limit_value="1000/minute")
async def delete_item(
    request: Request, id: UUID = Path(description="Идентификатор", example="3fa85f64-5717-4562-b3fc-2c963f66a333")
):
    await delete_item_sql(id)
    return SuccessfulResponse(details="Удаление прошло успешно.")


@imports_router.get("/nodes/{id}", response_model=ShopUnit, status_code=status.HTTP_200_OK)
@limiter.limit(limit_value="100/minute")
async def get_item(
    request: Request, id: UUID = Path(description="Идентификатор", example="3fa85f64-5717-4562-b3fc-2c963f66a333")
):
    nodes = format_nodes(await get_nodes_sql(id))
    return nodes


@imports_router.get("/sales", response_model=ShopUnitStatisticResponse, status_code=status.HTTP_200_OK)
@limiter.limit(limit_value="100/minute")
async def get_sales(request: Request, date: datetime = Query(description="Текущее время")):
    item = format_sales(await get_sales_sql(date), ShopUnitStatisticUnit)
    return item
