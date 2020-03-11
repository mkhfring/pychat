
from bddrest.authoring import when, Update, Remove, status

from jaguar.models.membership import Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestAddToContact(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user = Member(
            email='user@example.com',
            title='user',
            access_token='access token',
            reference_id=1
        )
        user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token',
            reference_id=2
        )
        contact1 = Member(
            email='contact1@example.com',
            title='contact1',
            access_token='access token',
            reference_id=3
        )
        contact2 = Member(
            email='contact2@example.com',
            title='contact2',
            access_token='access token',
            reference_id=4
        )
        user.contacts.append(contact2)
        contact1.contacts.append(user2)
        session.add_all([user,contact1])
        session.commit()

    def test_add_user_to_contact(self):
        self.login('user@example.com')

        with cas_mockup_server(), self.given(
            'Add a user to contacts',
            '/apiv1/contacts',
            'ADD',
           form=dict(userId=3),
        ):
            assert status == 200
            session = self.create_session()
            user = session.query(Member).filter(Member.id == 1).one()
            assert len(user.contacts) == 2

            when('The user id already added to contact', form=Update(userId=2))
            assert status == '603 Already Added To Contacts'

            when('Try to add not existing user', form=Update(userId=6))
            assert status == '611 Member Not Found'

            when(
                'Try to request with invalid user id',
                form=Update(userId='invalid')
            )
            assert status == '705 Invalid Member Id'

            when('Request without issuing userId', form=Remove('userId'))
            assert status == '709 Member Id Is Required'

            when('Trying to pass the unauthorized request', authorization=None)
            assert status == 401

