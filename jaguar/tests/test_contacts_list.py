
from bddrest.authoring import response, when, Update, status

from jaguar.models.membership import Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestListContact(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user = Member(
            email='user@example.com',
            title='user',
            access_token='access token',
            reference_id=1
        )
        contact1 = Member(
            email='contact1@example.com',
            title='contact1',
            access_token='access token',
            reference_id=2
        )
        contact2 = Member(
            email='contact2@example.com',
            title='contact2',
            access_token='access token',
            reference_id=3
        )

        # This contact is added to make sure the query works correctly
        contact3 = Member(
            email='contact3@example.com',
            title='contact3',
            access_token='access token',
            show_email=True,
            reference_id=4
        )
        user.contacts = [contact1, contact2]
        contact1.contacts.append(contact3)
        session.add(user)
        session.commit()

    def test_list_contacts(self):
        self.login('user@example.com')

        with cas_mockup_server(), self.given(
            'List a user contacts',
            '/apiv1/contacts',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('Try to sort the response', query=dict(sort='title'))
            assert len(response.json) == 2
            assert response.json[0]['title'] == 'contact1'

            when(
                'Try to sort the response in descending order',
                query=dict(sort='-title')
            )
            assert response.json[0]['title'] == 'contact2'

            when(
                'Try to filter the response using title',
                query=dict(title='contact2')
            )
            assert len(response.json) == 1
            assert response.json[0]['title'] == 'contact2'

            when(
                'Try to filter the response ignoring a title',
                query=dict(title='!contact2')
            )
            assert len(response.json) == 1
            assert response.json[0]['title'] != 'contact2'

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['title'] == 'contact2'

            when(
                'Test sorting before pagination',
                query=dict(sort='-title', take=1, skip=1)
            )
            assert response.json[0]['title'] == 'contact1'

            when('An unauthorized request', authorization=None)
            assert status == 401

