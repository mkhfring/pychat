import asyncio
from typing import Callable

import ujson
from nanohttp import settings

from ..redis_ import create_blocking_redis, create_async_redis


_blocking_redis = None
_async_redis = None


def blocking_redis():
    global _blocking_redis
    if _blocking_redis is None:
        _blocking_redis = create_blocking_redis(settings.messaging.redis)

    return _blocking_redis


async def async_redis():
    global _async_redis
    if _async_redis is None:
        _async_redis = await create_async_redis(settings.messaging.redis)

    return _async_redis


def push(queue, message):
    blocking_redis().lpush(queue, ujson.dumps(message))


async def push_async(queue: str, message: str):
    await (await async_redis()).lpush(queue, ujson.dumps(message))


async def pop_async(queue):
    encoded_message = await (await async_redis()).rpop(queue)
    return ujson.loads(encoded_message) if encoded_message else None


async def bpop_async(queue):
    return await (await async_redis()).brpop(queue)


async def flush_all_async():
    await (await async_redis()).flushdb()


async def dispose_async():
    global _async_redis
    if _async_redis and not _async_redis.closed \
            and _async_redis.connection._loop.is_running():
        _async_redis.close()
    _async_redis = None

