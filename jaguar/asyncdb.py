import asyncio
import asyncpg

from nanohttp import settings


_connection = None


async def get_connection(url=None):
    global _connection
    if _connection is None:
        _connection = await asyncpg.connect(url or settings.db.url)

    return _connection


async def close_connection():
    global _connection
    if _connection is None:
        return

    await _connection.close()

    _connection = None



async def get_members_by_target(target_id):
    query = '''
    SELECT m.id, m.reference_id
    FROM member m
    LEFT OUTER JOIN target_member tm ON m.id = tm.member_id
    WHERE tm.target_id = $1
    '''
    connection = await get_connection()
    members = await connection.fetch(query, target_id)
    return members


async def get_member_id_by_reference_id(reference_id):
    query = '''
    SELECT m.id
    FROM member m
    WHERE m.reference_id = $1
    '''
    return await (await get_connection()).fetchval(query, reference_id)



