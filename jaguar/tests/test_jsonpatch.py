from bddrest import status, response, when

from jaguar.models import Member, Room
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestJsonPatch(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        cls.user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token2',
            reference_id=3
        )
        session.add(cls.user2)
        cls.room = Room(
            title='example',
            members=[user1]
        )
        session.add(cls.room)
        session.commit()

    def test_patch(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'Testing the patch method on APIv1',
            verb='PATCH',
            url='/apiv1',
            json=[
                dict(
                    op='MENTION',
                    path=f'targets/{self.room.id}/mentions',
                    value={
                        'body': 'sample message',
                        'originTargetId': self.room.id
                    }
                ),
                dict(
                    op='MENTION',
                    path=f'members/{self.user2.id}/mentions',
                    value={'body': 'abc', 'originTargetId': self.room.id}
                ),
            ]
        ):
            assert status == 200
            assert len(response.json) == 2
            assert response.json[0]['id'] is not None
            assert response.json[1]['id'] is not None

            when(
                'One of requests response faces non 200 OK',
                json=[
                    dict(
                        op='MENTION',
                        path='targets/0/mentions',
                        value={}
                    )
                ]
            )
            assert status == 404

