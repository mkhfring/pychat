import json
import pytest

from jaguar.messaging import queues
from jaguar.messaging.tests.conftest import AsyncTest


class TestQueueManager(AsyncTest):

    @pytest.mark.asyncio
    async def test_push_pop_async(self, asyncpg):
        queue_name = 'test_queue'
        envelop = {
            'targetId': 1,
            'message':
            'sample message'
        }
        await queues.push_async(queue_name, envelop)

        message = await queues.pop_async(queue_name)
        assert message == envelop


