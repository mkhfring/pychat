from typing import Dict

import aioredis
from nanohttp import settings


from ..redis_ import create_async_redis

_redis = None


def _get_member_key(member_id):
    return f'member:{member_id}'


async def redis():
    global _redis
    if _redis is None:
        _redis = await create_async_redis(settings.messaging.redis)
    return _redis


async def register_session(member_id, session_id, queue):
    print(f'Registering session: {session_id} for member: {member_id}')
    await (await redis()).hset(
        _get_member_key(member_id),
        session_id,
        queue
    )


async def get_sessions(member_id: str) -> Dict[str, str]:
    return await (await redis()).hgetall(_get_member_key(member_id))



async def cleanup_session(member_id: str, session_id: str):
    await (await redis()).hdel(_get_member_key(member_id), session_id)


async def flush_all():
    await (await redis()).flushdb()


async def dispose():
    global _redis
    if _redis and _redis.connection._loop.is_running():
        _redis.close()
    _redis = None

