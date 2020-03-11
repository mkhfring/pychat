from bddrest.authoring import given, when, status, response, Update, Remove

from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server
from jaguar.models import Member, Room


class TestKickFromRoom(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user1 = Member(
            title='user1',
            email='user1@example.com',
            access_token='access token1',
            reference_id=2,
        )
        cls.user2 = Member(
            title='user2',
            email='user2@example.com',
            access_token='access token2',
            reference_id=3,
        )
        cls.user3 = Member(
            title='user3',
            email='user3@example.com',
            access_token='access token3',
            reference_id=4,
        )
        session.add(cls.user3)
        cls.room = Room(title='room', members=[user1, cls.user2])
        session.add(cls.room)
        session.commit()

    def test_kick_member(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            f'Kick a member from a room',
            f'/apiv1/rooms/id:{self.room.id}',
            f'KICK',
            form=dict(memberId=self.user2.reference_id)
        ):
            assert status == 200
            assert len(response.json['memberIds']) == 1

            when(
                'Member not a member of the room',
                form=Update(memberId=self.user3.reference_id)
            )
            assert status == '617 Not A Member'

            when('Member not found', form=Update(memberId=5))
            assert status == '611 Member Not Found'

            when('Try to pass without memberId', form=Remove('memberId'))
            assert status == '709 Member Id Is Required'

            when('Member id is invalid', form=Update(memberId='user1'))
            assert status == '705 Invalid Member Id'

            when('Request with bad room id', url_parameters=Update(id='room'))
            assert status == 404

            when('Try to pass an Unauthorized request', authorization=None)
            assert status == 401

