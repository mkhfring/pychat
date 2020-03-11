import io
from os.path import join, dirname, abspath

from bddrest.authoring import when, Update, status, response
from nanohttp import settings

from jaguar.models import Member, Room, Direct
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


THIS_DIR = abspath(join(dirname(__file__)))
TEXT_PATH = join(THIS_DIR, 'stuff', 'text_file.txt')
IMAGE_PATH = join(THIS_DIR, 'stuff', '150x150.png')
EXECUTABLE_PATH = join(THIS_DIR, 'stuff', 'putty.exe')
DLL_PATH = join(THIS_DIR, 'stuff', 'file.dll')
MAXIMUM_IMAGE_PATH = join(THIS_DIR, 'stuff', 'maximum-length.jpg')


class TestFileSharing(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        cls.room = Room(
            title='example',
            type='room',
            members=[cls.user1],
        )
        session.add(cls.room)
        session.commit()

    def test_attach_file_to_message(self):
        self.login(self.user1.email)

        with cas_mockup_server(), open(IMAGE_PATH, 'rb') as f, self.given(
            f'Send a message to a target',
            f'/apiv1/targets/id:{self.room.id}/messages',
            f'SEND',
            multipart=dict(
                body='hello world!',
                mimetype='image/png',
                attachment=io.BytesIO(f.read())
            )
        ):
            assert status == 200
            assert response.json['body'] == 'hello world!'
            assert response.json['isMine'] is True
            assert 'attachment' in response.json

            with open(TEXT_PATH, 'rb') as f:
                when(
                    'Mime type does not match content type',
                    multipart=Update(attachment=io.BytesIO(f.read()))
                )
                assert status == 200

            with open(MAXIMUM_IMAGE_PATH, 'rb') as f:
                when(
                    'Image size is more than maximum length',
                    multipart=Update(
                        mimetype='image/jpeg',
                        attachment=io.BytesIO(f.read()))
                )
                assert status == 413

            settings.attachements.messages.files.max_length = 800
            with open(EXECUTABLE_PATH, 'rb') as f:
                when(
                    'Image size is more than maximum length',
                    multipart=Update(
                        mimetype='image/jpeg',
                        attachment=io.BytesIO(f.read()))
                )
                assert status == '415 Unsupported Media Type'

            with open(DLL_PATH, 'rb') as f:
                when(
                    'Image size is more than maximum length',
                    multipart=Update(
                        mimetype='image/jpeg',
                        attachment=io.BytesIO(f.read()))
                )
                assert status == '415 Unsupported Media Type'

