from api.db import *
from api.db_connect import database
from .models import *


async def get_streams():
    query = Streams.select()
    return await database.fetch_all(query)


async def get_stream(stream_id: int):
    query = Streams.select().where(Streams.c.stream_id == stream_id)
    return await database.fetch_one(query)


async def update_stream(stream_id: int, stream: StreamUpdate):
    query = Streams.update().where(Streams.c.stream_id == stream_id).values(
        **stream.dict(exclude_unset=True))
    return await database.execute(query)


async def delete_stream(stream_id: int):
    query = Streams.delete().where(Streams.c.stream_id == stream_id)
    return await database.execute(query)


async def create_stream(stream: StreamIn):
    query = Streams.insert().values(**stream.dict(exclude_unset=True))
    return await database.execute(query)
