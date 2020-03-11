import io
from os.path import abspath, join, dirname

from bddrest.authoring import when, status, response, Update, Remove
from sqlalchemy_media import StoreManager
from nanohttp import settings

from jaguar.models import Member, Message, Room
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


THIS_DIR = abspath(join(dirname(__file__)))
IMAGE_PATH = join(THIS_DIR, 'stuff', '150x150.png')
DLL_PATH = join(THIS_DIR, 'stuff', 'file.dll')
MAXIMUM_IMAGE_PATH = join(THIS_DIR, 'stuff', 'maximum-length.jpg')


class TestReplyMessage(AutoDocumentationBDDTest):
    @classmethod
    def mockup(cls):
        session = cls.create_session(expire_on_commit=True)
        with StoreManager(session):
            with open(IMAGE_PATH, 'rb') as f:
                cls.message1 = Message(
                    body='This is message 1',
                    mimetype='image/png',
                    attachment=io.BytesIO(f.read()),
                )
                cls.message2 = Message(
                    body='This is message 2',
                    mimetype='text/plain'
                )
                user = Member(
                    title='user',
                    email='user@example.com',
                    access_token='access token',
                    reference_id=1
                )
                session.add(user)
                user1 = Member(
                    title='user1',
                    email='user1@example.com',
                    access_token='access token1',
                    reference_id=2,
                    messages=[cls.message1, cls.message2]
                )
                cls.room = Room(
                    title='room',
                    messages=[cls.message1, cls.message2],
                    members=[user1]
                )
                session.add(cls.room)
                cls.message2.soft_delete()
                session.commit()

    def test_reply_a_message(self):
        self.login('user@example.com')

        with cas_mockup_server(), self.given(
            f'Reply message 1',
            f'/apiv1/messages/id:{self.message1.id}',
            f'REPLY',
            multipart=dict(
                body='This is a reply to message1',
            )
        ):
            assert status == 200
            assert response.json['replyRoot'] == self.message1.id
            assert response.json['replyTo']['body'] == 'This is message 1'
            assert len(self.room.messages) == 3

            when('Requested message not found', url_parameters=Update(id=4))
            assert status == 404

            when(
                'Request a message with invalid message id',
                url_parameters=Update(id='message1')
            )
            assert status == 404

            when(
                'Try to reply with unsopported media type',
                multipart=Update(mimetype='video/3gpp')
            )
            assert status == 415

            when(
                'Try to send reply with long text',
                multipart=Update(body=(65536 + 1) * 'a')
            )
            assert status == '702 Must be less than 65536 charecters'

            when('Remove body from the form', multipart=Remove('body'))
            assert status == '712 Message Body Required'

            when(
                'Requested message is already deleted',
                url_parameters=Update(id=self.message2.id)
            )
            assert status == '616 Message Already Deleted'

            with open(IMAGE_PATH, 'rb') as f:
                when(
                    'Replay message with attachment',
                    multipart=Update(attachment=io.BytesIO(f.read()))
                )
                assert status == 200

            with open(MAXIMUM_IMAGE_PATH, 'rb') as f:
                when(
                    'Attachment is more than maximum length',
                    multipart=Update(attachment=io.BytesIO(f.read()))
                )
                assert status == 413

            settings.attachements.messages.files.max_length = 800
            with open(DLL_PATH, 'rb') as f:
                when(
                    'Replay a message with unsupported media type attachment',
                    multipart=Update(attachment=io.BytesIO(f.read()))
                )
                assert status == '415 Unsupported Media Type'

            when('Try to pass an unauthorized request', authorization=None)
            assert status == 401

