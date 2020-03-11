import io
from os.path import abspath, join, dirname

from bddrest.authoring import when, status, response, Update
from sqlalchemy_media import StoreManager

from jaguar.models import Member, Message, Room
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


THIS_DIR = abspath(join(dirname(__file__)))
IMAGE_PATH = join(THIS_DIR, 'stuff', '150x150.png')


class TestEditMessage(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        with StoreManager(session):
            with open(IMAGE_PATH, 'rb') as f:
                cls.message1 = Message(
                    body='This is message 1',
                    mimetype='text/plain',
                    attachment=io.BytesIO(f.read()),
                )
                message2 = Message(
                    body='This is message 2',
                    mimetype='text/plain',
                )
                cls.message3 = Message(
                    body='This is message 3',
                    mimetype='text/plain',
                )
                cls.user1 = Member(
                    email='user1@example.com',
                    title='user1',
                    access_token='access token1',
                    reference_id=2,
                    messages=[cls.message1, message2, cls.message3]
                )
                cls.user2 = Member(
                    email='user2@example.com',
                    title='user2',
                    access_token='access token2',
                    reference_id=3
                )
                session.add(cls.user2)

                room = Room(
                    title='room',
                    type='room',
                    members=[cls.user1],
                    messages=[cls.message1, message2, cls.message3]
                )
                session.add(room)
                cls.message3.soft_delete()
                session.commit()

    def test_edit_the_message(self):
        self.login(self.user1.email)

        with cas_mockup_server(), self.given(
            f'Try to edit a message',
            f'/apiv1/messages/id:{self.message1.id}',
            f'EDIT',
            form=dict(body='Message 1 is edited')
        ):
            assert status == 200
            assert response.json['body'] == 'Message 1 is edited'
            assert response.json['id'] == 1
            assert response.json['attachment'] is not None

            when('The message not exists', url_parameters=Update(id=0))
            assert status == 404

            when(
                'Trying to pass using invalid message id',
                url_parameters=Update(id='not-integer')
            )
            assert status == 404

            when(
                'Try to send long text',
                form=Update(body=(65536 + 1) * 'a')
            )
            assert status == '702 Must be less than 65536 charecters'

            when(
                'Try to edit a deleted message',
                url_parameters=Update(id=self.message3.id)
            )
            assert status == '616 Message Already Deleted'

            self.logout()
            self.login(self.user2.email)

            when(
                'Not allowed to edit the message',
                authorization=self._authentication_token,
            )
            assert status == 403

            when('Try to pass an unauthorized request', authorization=None)
            assert status == 401

