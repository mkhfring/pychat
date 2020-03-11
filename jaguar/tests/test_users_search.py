from bddrest.authoring import given, when, status, Update, response, Remove

from jaguar.models import Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestSearchMember(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        cls.user2 = Member(
            email='user2@gmail.com',
            title='user2',
            access_token='access token2',
            reference_id=3
        )
        session.add_all([cls.user1, cls.user2])
        session.commit()

    def test_search_user(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'Search for a user',
            '/apiv1/members',
            'SEARCH',
            form=dict(query='Use'),
        ):
            assert status == 200
            assert response.json[0]['title'] == self.user2.title
            assert len(response.json) == 2

            when('Search using email', form=Update(query='exam'))
            assert status == 200
            assert len(response.json) == 1

            when('Search without query parameter', form=Remove('query'))
            assert status == '708 Search Query Is Required'

            when(
                'Search string must be less than 20 charecters',
                form=Update(
                    query= \
                        'The search string should be less than 20 charecters'
                )
            )
            assert status == '702 Must Be Less Than 20 Charecters'

            when('Try to sort the respone', query=dict(sort='id'))
            assert len(response.json) == 2
            assert response.json[0]['id'] == 1

            when(
                'Trying ro sort the response in descend ordering',
                 query=dict(sort='-id')
            )
            assert response.json[0]['id'] == 2

            when('Filtering the response', query=dict(title='user2'))
            assert len(response.json) == 1
            assert response.json[0]['title'] == 'user2'

            when(
                'Trying to filter the response ignoring the title',
                 query=dict(title='!user2')
            )
            assert len(response.json) == 1
            assert response.json[0]['title'] != 'user2'

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.user1.title

            when(
                'Sort before pagination',
                query=dict(sort='-id', take=3, skip=1)
            )
            assert len(response.json) == 1
            assert response.json[0]['title'] == 'user1'

    def test_request_with_query_string(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'Test request using query string',
            '/apiv1/members',
            'SEARCH',
            query=dict(query='user')
        ):
            assert status == 200
            assert len(response.json) == 2

            when('An unauthorized search', authorization=None)
            assert status == 401

