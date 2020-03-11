from restfulpy.orm import DBSession
from restfulpy.principal import JwtPrincipal, JwtRefreshToken
from nanohttp import context
from bddrest.authoring import response, when, Update, Remove, status

from jaguar.models.membership import Member
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestRoom(AutoDocumentationBDDTest):

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

    def test_create_room(self):
        self.login('user@example.com')

        with cas_mockup_server(), self.given(
            'Creating a room',
            '/apiv1/rooms',
            'CREATE',
            form=dict(title='example'),
        ):
            assert status == 200
            assert response.json['title'] == 'example'
            assert response.json['ownerId'] == 1
            assert len(response.json['administratorIds']) == 1
            assert len(response.json['memberIds']) == 1

            when(
                'The room title exceed maximum length',
                form=Update(
                    title='a'*(50+1)
                )
            )
            assert status == '702 Must Be Less Than 50 Charecters'

            when('Title is required', form=Remove('title'))
            assert status == '703 Room Title Is Required'

            when('The room already exist')
            assert status == '615 Room Already Exists'

