from datetime import datetime, timedelta
from uuid import UUID
from app.db.db import DB
from app.exceptions import NotFoundException
from asyncpg import Record
from app.models import ShopUnitImportRequest
from app.queries.models import check_id, check_parent_id
from app.utils import format_row_update

sql_update_count = """UPDATE items
                      SET count_offer =
                                      (SELECT count(id)
                                       FROM items i
                                       WHERE shop_type = 'OFFER'
                                        AND parent_id = $1) + coalesce(
                                                                        (SELECT SUM(count_offer)
                                                                         FROM items i
                                                                         WHERE  shop_type = 'CATEGORY'
                                                                          AND parent_id = $1 ) ,0)

                      WHERE items.id = $1"""


sql_update_price = """ UPDATE items
                       SET price = (coalesce((SELECT SUM(price)
                                              FROM items i
                                              WHERE shop_type = 'OFFER'
                                                AND parent_id = $1),0)
                                    + coalesce(
                                              (SELECT SUM(price * count_offer )
                                               FROM items i
                                               WHERE  shop_type = 'CATEGORY'
                                               AND parent_id = $1),0) )/NULLIF(count_offer,0)
                        WHERE items.id = $1
                        RETURNING shop_type, id, name_item, price, parent_id, date_update;"""
                        
                        
sql_insert_snapshot = """INSERT INTO items_snapshot (shop_type, id, name_item, price, parent_id, date_update)
                         VALUES($1,$2,$3,$4,$5,$6)
                         ON CONFLICT ON CONSTRAINT pk_is
                         DO UPDATE SET name_item = $3, price = $4, parent_id = $5;"""
                         

async def add_items_sql(items: ShopUnitImportRequest) -> None:
    sql = """INSERT INTO items (shop_type, id, name_item, price, parent_id, date_update, count_offer)
             VALUES($1,$2,$3,$4,$5,$6,0)
             ON CONFLICT (id)
             DO UPDATE SET name_item = $3, price = coalesce($4, items.price), parent_id = $5, date_update= $6;
             """
    sql_update_time = """UPDATE items
                         SET date_update = $1
                         WHERE items.id = $2 """
    for item in items.items:
        async with DB.con.acquire() as connection:
            async with connection.transaction():
                await check_parent_id(item.parentId)
                await check_id(item.id, item.type)
                await connection.execute(
                    sql, item.type, item.id, item.name, item.price, item.parentId, items.updateDate
                )
                await connection.execute(
                        sql_insert_snapshot, item.type, item.id, item.name, item.price, item.parentId, items.updateDate
                )
                parentid = item.parentId
                while parentid is not None:
                    await connection.execute(sql_update_count, parentid)
                    await connection.execute(sql_update_time, items.updateDate, parentid)
                    parentid, snapshot_item  = format_row_update(await connection.fetchrow(sql_update_price, parentid))
                    await connection.execute(
                        sql_insert_snapshot, snapshot_item.type, snapshot_item.id, snapshot_item.name, snapshot_item.price, snapshot_item.parentId, items.updateDate
                    )


async def delete_item_sql(id: UUID) -> None:
    sql = """DELETE FROM items
             WHERE id = $1
             RETURNING *;"""
    async with DB.con.acquire() as connection:
        async with connection.transaction():
            check = await connection.fetchrow(sql, id)
            if not check:
                raise NotFoundException(error="Item not found")
            parentid = check["parent_id"]
            while parentid is not None:
                await connection.execute(sql_update_count, parentid)
                parentid, snapshot_item  = format_row_update(await connection.fetchrow(sql_update_price, parentid))


async def get_nodes_sql(id: UUID) -> Record:
    sql = """
            WITH RECURSIVE r AS
               (SELECT i.shop_type,
                       i.id,
                       i.name_item,
                       i.parent_id,
                       i.date_update,
                       i.price
                FROM items i
                WHERE i.id = $1
                UNION SELECT i.shop_type,
                             i.id,
                             i.name_item,
                             i.parent_id,
                             i.date_update,
                             i.price
                FROM items i
                JOIN r ON i.parent_id =r.id)
            SELECT *
            FROM r
          """
    items = await DB.con.fetch(sql, id)
    if not items:
        raise NotFoundException(error="Item not found")
    return items


async def get_sales_sql(date: datetime) -> Record:
    date_end = date - timedelta(hours=24)
    sql = """SELECT shop_type, id, name_item , parent_id , date_update , price
             FROM items
             WHERE shop_type = 'OFFER' and date_update <= $1 and date_update >= $2 """
    items = await DB.con.fetch(sql, date, date_end)
    return items


async def get_statistic_sql(id: UUID, dateStart: datetime, dateEnd: datetime)-> Record:
    sql = """SELECT shop_type, id, name_item , parent_id , date_update , price
             FROM items_snapshot
             WHERE id = $3 and date_update < $2 and date_update >= $1 """
    items = await DB.con.fetch(sql, dateStart, dateEnd, id)
    return items



