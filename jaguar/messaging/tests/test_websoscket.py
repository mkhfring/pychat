import pytest
from restfulpy.principal import JwtPrincipal

from jaguar.messaging import sessions
from jaguar.models import Member
from jaguar.messaging.tests.conftest import AsyncTest


class TestWebsocketConnection(AsyncTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            email='member@example.com',
            title='member',
            access_token='access token',
            reference_id=1
        )
        contact1 = Member(
            email='contact1@example.com',
            title='contact1',
            access_token='access token',
            reference_id=2
        )
        cls.member.contacts.append(contact1)
        session.add(cls.member)
        session.commit()


    @pytest.mark.asyncio
    async def test_websocket(self, websocket_session, asyncpg):
        self.login('member@example.com')

        async with websocket_session(token=self._authentication_token) as ws:
            token = JwtPrincipal.load(self._authentication_token)
            member_id = self.member.id
            session_id = token.session_id.encode()

            member_sessions = await sessions.get_sessions(member_id)
            assert len(member_sessions) == 1
            assert member_sessions == {session_id: b'jaguar_websocket_server_1'}
            await ws.send_str('close')
            assert await ws.receive_str() == 'closing'

            active_sessions = await sessions.get_sessions(member_id)
            assert len(active_sessions) == 0

