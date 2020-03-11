import asyncio

import redis
import aioredis


def create_blocking_redis(params):
    return redis.StrictRedis(**params)


async def create_async_redis(params):
    return await aioredis.create_redis(
        (params.host, params.port),
        db=params.db,
        password=params.password,
        loop=asyncio.get_event_loop()
    )


