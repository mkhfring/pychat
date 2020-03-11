
from bddrest.authoring import response, when, Update, Remove, status

from jaguar.models.membership import Member
from jaguar.models.target import Room, Direct
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestListSubscribeTarget(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user = Member(
            email='user@example.com',
            title='user',
            access_token='access token',
            reference_id=1
        )
        user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token2',
            reference_id=3
        )
        session.add(user2)
        direct = Direct(members=[user, user1])
        session.add(direct)
        cls.room1 = Room(title='room1', members=[user])
        session.add(cls.room1)
        room2 = Room(title='room2', members=[user1])
        session.add(room2)
        room3 = Room(title='room3', members=[user, user1])
        session.add(room3)
        session.commit()

    def test_list_subscribe_target(self):
        self.login('user@example.com')

        with cas_mockup_server(), self.given(
            'List targets a user subscribe to',
            '/apiv1/subscribetargets',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 3
            assert response.json[0]['id'] == 1

            when('Sorting the response descending', query=dict(sort='-id'))
            assert len(response.json) == 3
            assert response.json[0]['id'] == 4

            when('testing pagination', query=dict(sort='id', take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['id'] == 2

            when(
                'Sorting befor pagination',
                query=dict(sort='-id', take=1, skip=1)
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == 2

            when('Filtering the answer', query=dict(id=self.room1.id))
            assert len(response.json) == 1
            assert response.json[0]['title'] == 'room1'

            when('Try to pass an Unauthorized request', authorization=None)
            assert status == 401

