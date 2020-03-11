from bddrest.authoring import status, given, when, Update, response

from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server
from jaguar.models import Member, member_block


class TestDirect(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token',
            reference_id=1
        )
        blocker = Member(
            email='blocker@example.com',
            title='blocker',
            access_token='access token4',
            reference_id=5
        )
        blocker.blocked_members.append(cls.user1)
        session.add_all([blocker, user2])
        session.commit()

    def test_creat_token(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'Try to create a direct with a user',
            '/apiv1/directs',
            'CREATE',
            form=dict(userId=3)
        ):
            assert status == 200
            assert response.json['type'] == 'direct'

            when('The user not exists', form=Update(userId=5))
            assert status == '611 Member Not Found'

            when(
                'Try to pass invalid user id in the form',
                form=Update(userId='Invalid')
            )
            assert status == '705 Invalid Member Id'

            when('Try to pass empty form', form=None)
            assert status == '710 Empty Form'

            when('Blocked user tries to create a direct', form=Update(userId=1))
            assert status == '613 Not Allowed To Create Direct With This Member'

            self.logout()
            self.login('blocker@example.com')

            when(
                'Try to create a direct with a blocked user',
                form=Update(userId=self.user1.id),
                authorization=self._authentication_token
            )
            assert status == '613 Not Allowed To Create Direct With This Member'

            when('Try to pass an unauthorized request', authorization=None)
            assert status == 401

