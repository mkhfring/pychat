import pytest

from jaguar.messaging import sessions, router, queues
from jaguar.models import Member, Room
from jaguar.messaging.tests.conftest import AsyncTest


class TestMessageRouter(AsyncTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member1 = Member(
            email='member1@example.com',
            title='member1',
            access_token='access token',
            reference_id=1
        )
        cls.member2 = Member(
            email='member2@example.com',
            title='member2',
            access_token='access token',
            reference_id=2
        )
        cls.member3 = Member(
            email='member3@example.com',
            title='member3',
            access_token='access token',
            reference_id=3
        )
        session.add(cls.member3)

        cls.room = Room(
            title='room1',
            members=[cls.member1, cls.member2]
        )
        session.add(cls.room)
        session.commit()

    @pytest.mark.asyncio
    async def test_route(self, asyncpg):
        queue_name = 'test_queue'
        session_id1 = '1'
        session_id2 = '2'

        await sessions.register_session(
            self.member1.id,
            session_id1,
            queue_name
        )

        await sessions.register_session(
            self.member3.id,
            session_id2,
            queue_name
        )

        envelop = {
            'targetId': self.room.id,
            'message': 'sample message',
            'senderId': 1,
            'isMine': True
        }
        await router.route(envelop)

        message = await queues.pop_async(queue_name)
        assert message == envelop

        seen_envelop = {
            'type': 'seen',
            'targetId': self.room.id,
            'message': 'sample message',
            'senderId': 1,
            'isMine': True
        }

        await router.route(seen_envelop)

        message = await queues.pop_async(queue_name)
        assert message == seen_envelop

        mention = {
            'type': 'mention',
            'mentionedMember': self.member3.id,
            'targetId': self.room.id,
            'message': 'sample message',
            'senderId': 1,
            'isMine': True
        }

        await router.route(mention)

        message = await queues.pop_async(queue_name)
        assert message == mention

