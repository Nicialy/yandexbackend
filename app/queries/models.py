from uuid import UUID

from fastapi.exceptions import RequestValidationError
from app.db.db import DB
from app.models import ShopUnitType


async def check_parent_id(parent_id: UUID) -> None:
    if parent_id is not None:
        sql = """SELECT shop_type
                 FROM items
                 WHERE id = $1 """
        type = await DB.con.fetchval(sql, parent_id)
        if type != ShopUnitType.CATEGORY.value:
            raise RequestValidationError(errors="Validation Failed")


async def check_id(id: UUID, shop_type: ShopUnitType) -> None:
    sql = """SELECT shop_type
             FROM items
             WHERE id = $1 """
    type_sql = await DB.con.fetchval(sql, id)
    if type_sql is not None and type_sql != shop_type:
        raise RequestValidationError(errors="Validation Failed")
