import ujson
from nanohttp import settings
from bddrest.authoring import when, Update, status, response, Remove

from jaguar.models import Member, Room
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server, \
    maestro_mockup_server, maestro_server_status


class TestSendMessage(AutoDocumentationBDDTest):

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
            access_token='access token2',
            reference_id=3
        )
        session.add(user2)

        cls.room = Room(
            title='example',
            members=[cls.user1]
        )
        session.add(cls.room)
        session.commit()

    def test_send_message_to_target(self):
        self.login(self.user1.email)

        with cas_mockup_server(), maestro_mockup_server(), self.given(
            f'Send a message to a target',
            f'/apiv1/targets/id:{self.room.id}/messages',
            f'SEND',
            form=dict(body='hello world!')
        ):
            assert status == 200
            assert response.json['body'] == 'hello world!'
            assert response.json['isMine'] is True
            assert response.json['mimetype'] == 'text/plain'
            assert response.json['senderReferenceId'] == self.user1.reference_id

            when('Invalid target id', url_parameters=Update(id='Invalid'))
            assert status == '706 Invalid Target Id'

            when('Target does not exist', url_parameters=Update(id=0))
            assert status == '404 Target Not Exists'

            when(
                'Try to send unsopported media type',
                form=Update(mimetype='video/3gpp')
            )
            assert status == 415

            when(
                'Try to send long text',
                form=Update(body=(65536 + 1) * 'a')
            )
            assert status == '702 Must be less than 65536 charecters'

            when('Remove body from the form', form=Remove('body'))
            assert status == 400

            when('Try to pass an unauthorized request', authorization=None)
            assert status == 401

            settings.webhooks.sent.timeout = 0.1
            when('Request to Dolphin is timeout')
            assert status == 200

            settings.webhooks.sent.timeout = 30
            settings.webhooks.sent.url = 'http://localhost:1'
            when('Connection is failed')
            assert status == 200

    def test_send_message_as_auditlog(self):
        self.login(self.user1.email)
        body = dict(action='Create', attribute='a', new=1, old=2)
        mimetype = 'application/x-auditlog'

        with cas_mockup_server(), self.given(
            None,
            f'/apiv1/targets/id:{self.room.id}/messages',
            f'SEND',
            json=dict(body=ujson.dumps(body), mimetype=mimetype)
        ):
            assert status == 200
            assert response.json['body'] == body
            assert response.json['mimetype'] == mimetype

