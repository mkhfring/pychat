import pytest

from jaguar.messaging import queues, sessions, router
from jaguar import asyncdb
from jaguar.models import Member, Room
from jaguar.messaging.tests.conftest import AsyncTest


class TestAsyncDB(AsyncTest):

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
        cls.room = Room(
            title='room1',
            members=[cls.member1, cls.member2]
        )
        session.add(cls.room)
        session.commit()

    @pytest.mark.asyncio
    async def test_get_member_by_taget(self, asyncpg):
        members = await asyncdb.get_members_by_target(self.room.id)
        assert len(members) == 2
        assert set(m.get('id') for m in members) == set((
            self.member1.id,
            self.member2.id
        ))

