import asyncio
from async_generator import asynccontextmanager

import pytest
import aiohttp
from multidict import CIMultiDict
from aiohttp.web_runner import AppRunner, TCPSite
from nanohttp.tests.conftest import free_port
from nanohttp import settings

from jaguar.tests.helpers import AutoDocumentationBDDTest
from jaguar.messaging.websocket import app as websocket_application
from jaguar.messaging import queues, sessions, router
from jaguar import asyncdb


@pytest.fixture
async def websocket_server(loop, free_port):
    host = 'localhost'
    runner = AppRunner(websocket_application)
    await runner.setup()
    tcpsite = TCPSite(runner, host, free_port, shutdown_timeout=2)
    await tcpsite.start()

    yield tcpsite.name

    await runner.shutdown()
    await runner.cleanup()


@pytest.fixture
async def websocket_session(websocket_server):
    @asynccontextmanager
    async def connect(token=None, **kw):
        query_string = ''
        if token:
            query_string = f'token={token}'

        async with aiohttp.ClientSession() as session, \
                session.ws_connect(websocket_server + f'?{query_string}') as ws:
            yield ws
    yield connect

@pytest.fixture
async def asyncpg(loop):
    await sessions.dispose()
    await sessions.flush_all()
    await queues.dispose_async()
    await queues.flush_all_async()
    await asyncdb.close_connection()

    yield await asyncdb.get_connection(settings.db.test_url)

    await sessions.dispose()
    await sessions.flush_all()
    await queues.dispose_async()
    await queues.flush_all_async()
    await asyncdb.close_connection()


class AsyncTest(AutoDocumentationBDDTest):
    pass

