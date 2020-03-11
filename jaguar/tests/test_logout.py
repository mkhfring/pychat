
from bddrest.authoring import response, when, Remove, Update, status

from jaguar.models.membership import Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestLogout(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user = Member(
            email='user@example.com',
            title='user',
            access_token='access token',
            reference_id=1
        )
        session.add(user)
        session.commit()

    def test_logout_a_user(self):
        self.login('user@example.com')

        with cas_mockup_server(), self.given(
            'Log out a user',
            '/apiv1/tokens',
            'INVALIDATE',
        ):
            assert status == 200

            when('Try to access some authorize source', authorization=None)
            assert status == 401

