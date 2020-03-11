from bddrest.authoring import when, status, response

from jaguar.models import Envelop, Room, Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestEnvelop(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.envelop1 = Envelop(body='This is envelop 1')

        cls.envelop2 = Envelop(body='This is envelop 2')

        cls.envelop3 = Envelop(body='This is envelop 3')

        cls.envelop4 = Envelop(body='This is envelop 4')

        user1 = Member(
            email='user1@example.com',
            title='user',
            access_token='access token1',
            reference_id=2,
            messages=[cls.envelop1, cls.envelop2, cls.envelop3, cls.envelop4]
        )

        room1 = Room(
            title='room1',
            members=[user1],
            messages=[cls.envelop1, cls.envelop2, cls.envelop3, cls.envelop4]
        )
        session.add(room1)
        session.commit()

    def test_list(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'List envelops',
            '/apiv1/envelops',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 4

            when('Sort envelops', query=dict(sort='body'))
            assert response.json[0]['body'] == self.envelop1.body

            when(
                'Reverse sorting body content by alphabet',
                query=dict(sort='-body')
            )
            assert response.json[0]['body'] == self.envelop4.body

            when(
                'Filter envelops',
                query=dict(sort='id', body=self.envelop1.body)
            )
            assert response.json[0]['body'] == self.envelop1.body

            when(
                'List envelops except one of them',
                query=dict(sort='id', body=f'!{self.envelop1.body}')
            )
            assert response.json[0]['body'] == self.envelop2.body

            when('Envelop pagination', query=dict(sort='id', take=1, skip=2))
            assert response.json[0]['body'] == self.envelop3.body

            when(
                'Manipulate sorting and pagination',
                query=dict(sort='-body', take=1, skip=2)
            )
            assert response.json[0]['body'] == self.envelop2.body

            when('Request is not authorized', authorization=None)
            assert status == 401

