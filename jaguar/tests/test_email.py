from bddrest.authoring import response, when, Remove, Update

from jaguar.models.membership import Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestEmail(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user = Member(
            email='already.added@example.com',
            title='example',
            access_token='access token',
            reference_id=1
        )
        session.add(user)
        session.commit()

    def test_claim_email(self):
        with cas_mockup_server(), self.given(
            'claim a user',
            '/apiv1/emails',
            'CLAIM',
            form=dict(email='test@example.com')
        ):

            assert response.status == '200 OK'

            when(
                'The email is repeted',
                form=Update(email='already.added@example.com')
            )
            assert response.status == '601 The requested email address is ' \
                'already registered.'

            when(
                'The email format is invalid',
                form=Update(email='already.example.com')
            )
            assert response.status == '701 Invalid email format.'

            when('Request without email', form=Remove('email'))
            assert response.status == 400

