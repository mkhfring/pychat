from bddrest import when, status, response, Update

from jaguar.models import Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server
class TestGetMember(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        session.add(user1)
        user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token2',
            reference_id=3
        )
        session.add(user2)
        session.commit()

    def test_get_user_by_id(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'Get a user by her or his id',
            '/apiv1/members/id:1',
            'GET',
        ):
            assert status == 200
            assert response.json['title'] == 'user1'

            when('Member not found', url_parameters=Update(id='3'))
            assert status == 404

            when('Ivalid use id', url_parameters=Update(id='user1'))
            assert status == 404

            when('Try to pass unauthorize request', authorization=None)
            assert status == 401

