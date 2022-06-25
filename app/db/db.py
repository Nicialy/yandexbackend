import asyncpg
from app.settings import DATABASE_URL
from app.exceptions import InternalServerError


class DB:
    con: asyncpg.connection.Connection = None

    @classmethod
    async def connect_db(cls) -> None:
        try:
            cls.con = await asyncpg.create_pool(DATABASE_URL)
        except asyncpg.PostgresError as error:
            raise InternalServerError() from error

    @classmethod
    async def disconnect_db(cls) -> None:
        await cls.con.close()
