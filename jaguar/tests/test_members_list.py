from bddrest.authoring import when, status, response

from jaguar.models import Room, Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestListMembers(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2,
        )
        cls.user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token2',
            reference_id=3
        )
        cls.user3 = Member(
            email='user3@example.com',
            title='user3',
            access_token='access token3',
            reference_id=4,
        )
        cls.room1 = Room(
            title='room1',
            members=[cls.user1, cls.user2, cls.user3],
        )
        session.add(cls.room1)

        cls.room2 = Room(
            title='room2',
            members=[cls.user1, cls.user2],
        )
        session.add(cls.room2)
        session.commit()

    def test_list_members_of_target(self):
        self.login(self.user1.email)

        with cas_mockup_server(), self.given(
            'List members of a target',
            f'/apiv1/targets/id: {self.room1.id}/members',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when(
                'Target is not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(parameter='parameter')
            )
            assert status == '711 Form Not Allowed'

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 3
            assert response.json[0]['id'] == 1

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 3

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.user3.title

            when(
                'Sorting befor pagination',
                query=dict(sort='-id', take=2, skip=1)
            )
            assert len(response.json) == 2
            assert response.json[0]['id'] == 2

            when('Filtering the response', query=dict(id=self.user3.id))
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.user3.title

            when('Try to pass an Unauthorized request', authorization=None)
            assert status == 401

    def test_list_members(self):
        self.login(self.user1.email)

        with cas_mockup_server(), self.given(
            'List members of a target',
            f'/apiv1/members',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when(
                'There is parameter in form',
                form=dict(parameter='parameter')
            )
            assert status == '711 Form Not Allowed'

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 3
            assert response.json[0]['id'] == 1

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 3

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.user3.title

            when(
                'Sorting befor pagination',
                query=dict(sort='-id', take=2, skip=1)
            )
            assert len(response.json) == 2
            assert response.json[0]['id'] == 2

            when('Filtering the response', query=dict(id=self.user3.id))
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.user3.title

            when('Try to pass an Unauthorized request', authorization=None)
            assert status == 401

