from contextlib import contextmanager

from bddrest.authoring import given, status, response, when, Update, Remove
from restfulpy.principal import JwtPrincipal
from restfulpy.mockup import mockup_http_server
from restfulpy.authorization import authorize
from nanohttp import settings, json, context, action
from nanohttp import RegexRouteController

from jaguar.tests.helpers import AutoDocumentationBDDTest, MockupApplication, \
    cas_mockup_server, cas_server_status
from jaguar.models import Member



class Root(RegexRouteController):

    def __init__(self):
        return super().__init__([('/apiv1/resources', self.get),])

    @authorize
    @action
    def get(self):
        return 'Index'


class TestApplication(AutoDocumentationBDDTest):
    __controller_factory__ = Root

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        user1 = Member(
            email='user1@gmail.com',
            title='user1',
            reference_id=1,
            access_token='access token1'
        )
        session.add(user1)
        session.commit()

    def test_login_with_cas(self):
        token = JwtPrincipal(dict(
            email='user2@example.com',
            title='user2',
            referenceId=2
        )).dump().decode()
        self._authentication_token = token

        with cas_mockup_server():
            settings.merge(f'''
                oauth:
                  member:
                    url: {settings.tokenizer.url}/apiv1/members
                    verb: get
            ''')
            with self.given(
                title='Try to access an authorized resource',
                description='Members are got from the cas',
                url='/apiv1/resources',
                headers={'X-Oauth2-Access-Token: access token2'}
            ):
                assert status == 200
                mismathc_token = JwtPrincipal(dict(
                    email='user3@example.com',
                    title='user3',
                    referenceId=3
                )).dump().decode()

                when(
                    'Token not match the CAS member',
                    authorization=mismathc_token
                )
                assert status == 400

                when(
                    'Try to pass with bad token',
                    authorization='Invalid Token'
                )
                assert status == 400

                when(
                    'Try to access an unauthorized resource',
                    authorization=None
                )
                assert status == 401

                member_token = JwtPrincipal(dict(
                    email='user1@example.com',
                    title='user1',
                    referenceId=1
                )).dump().decode()
                when(
                    'Member exist in database',
                    authorization=member_token,
                    headers=Remove('X-Oauth2-Access-Token')
                )
                assert status == 200

                with cas_server_status('503 Service Not Available'):
                    when('CAS server is not available')
                    assert status == '800 CAS Server Not Available'

                with cas_server_status('500 Internal Service Error'):
                    when('CAS server faces with internal error')
                    assert status == '801 CAS Server Internal Error'

                with cas_server_status('404 Not Found'):
                    when('CAS server is not found')
                    assert status == '617 CAS Server Not Found'

