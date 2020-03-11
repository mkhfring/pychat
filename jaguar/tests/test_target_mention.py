from bddrest.authoring import status, when, given, response

from jaguar.models import Member, Room
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestMention(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        member1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        cls.room = Room(
            title='example',
            members=[member1]
        )
        session.add(cls.room)
        session.commit()

    def test_mention(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'Mention a target',
            f'/apiv1/targets/{self.room.id}/mentions',
            'MENTION',
            json=dict(body='abc', originTargetId=self.room.id)
        ):
            assert status == 200
            assert response.json['body'] == 'abc'

            when(
                'Origin target id is null',
                json=given | dict(originTargetId=None)
            )
            assert status == '718 Origin Target Id Is Null'

            when(
                'Origin target id is not in form',
                json=given - 'originTargetId'
            )
            assert status == '717 Origin Target Id Not In Form'

            when(
                'Origin target id is not found',
                json=given | dict(originTargetId=0)
            )
            assert status == '622 Target Not Found'

            when(
                'Body length is more than limit',
                json=given | dict(body=(65536 + 1) * 'a')
            )
            assert status == '702 Must be less than 65536 charecters'

            when('User is logged out', authorization=None)
            assert status == 401

