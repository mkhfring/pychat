import json
import asyncio
from os import path

import aiohttp
import itsdangerous
from aiohttp import web
from cas import CASPrincipal
from nanohttp import settings
from restfulpy.orm import DBSession
from restfulpy.configuration import configure as restfulpy_configure

from jaguar import asyncdb
from . import queues, sessions
from ..models import Member


async def authenticate(request):
    encoded_token = request.query.get('token');
    if encoded_token is None:
        raise web.HTTPUnauthorized()

    if encoded_token is None or not encoded_token.strip():
        raise web.HTTPUnauthorized()

    try:
        principal = CASPrincipal.load(encoded_token)
        return principal
    except itsdangerous.BadData:
        raise web.HTTPUnauthorized()


#https://aiohttp.readthedocs.io/en/stable/web_advanced.html#graceful-shutdown
async def websocket_handler(request):
    identity = await authenticate(request)

    # FIXME: async
    member_id = await asyncdb\
        .get_member_id_by_reference_id(identity.reference_id)

    if not member_id:
        raise web.HTTPUnauthorized()

    print('New session: %s has been connected' % identity.session_id)

    await sessions.register_session(
        member_id,
        identity.session_id,
        app_state()['queue_name']
    )

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print(f'Storing socket for session: {identity.session_id} for member: '\
          f'{member_id}')
    app_state()[identity.session_id] = ws

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.send_str('closing')
                break
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')
    await sessions.cleanup_session(member_id, identity.session_id)
    del app_state()[str(identity.session_id)]
    #await ws.close()
    return ws


async def worker(name):
    await sessions.flush_all()
    while True:
        message = await queues.pop_async(name)
        if not message:
            await asyncio.sleep(1)
            continue

        session_id = message['sessionId']
        print(f'Sending to session: {session_id}')
        ws = app_state().get(session_id)
        if ws is not None:
            await ws.send_json(message)



HERE = path.abspath(path.dirname(__file__))
ROOT = path.abspath(path.join(HERE, '../..'))


async def start_workers(app):
    queue_name = 'jaguar_websocket_server_1'
    loop = asyncio.get_event_loop()
    app_state()['queue_name'] = queue_name
    app_state()['message_dispatcher'] = loop.create_task(
        worker(queue_name)
    )


async def cleanup_background_tasks(app):
    #app_state()['message_dispatcher'].cancel()
    #await app_state()['message_dispatcher']
    await asyncdb.close_connection()


async def prepare_session_manager(app):
    await sessions.redis()


def app_state():
    return app['state']


app = web.Application()
app.add_routes([web.get('/', websocket_handler)])
app['state'] = {}
app.on_startup.append(prepare_session_manager)
app.on_startup.append(start_workers)

app.on_cleanup.append(cleanup_background_tasks)

