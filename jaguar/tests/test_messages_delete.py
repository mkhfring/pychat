from os.path import abspath, join, dirname

from bddrest.authoring import when, status, response, Update
from sqlalchemy_media import StoreManager

from jaguar.models import Member, Room, Message
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')


class TestDeleteMessage(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        cls.session = cls.create_session(expire_on_commit=True)
        with StoreManager(cls.session):
            cls.message1 = Message(
                body='This is message 1',
                mimetype='text/plain'
            )
            cls.message2 = Message(
                body='This is message 2',
                mimetype='text/plain'
            )
            cls.message3 = Message(
                body='This is message 3',
                mimetype='image/png',
                attachment=image_path
            )
            user = Member(
                email='user@example.com',
                title='user',
                access_token='access token',
                reference_id=1,
                messages=[cls.message1, cls.message3]
            )
            user1 = Member(
                email='user1@example.com',
                title='user1',
                access_token='access token1',
                reference_id=2,
                messages=[cls.message2]
            )
            user2 = Member(
                email='user2@example.com',
                title='user2',
                access_token='access token2',
                reference_id=3
            )
            room = Room(
                title='room',
                type='room',
                messages=[cls.message1, cls.message2, cls.message3],
                members=[user, user1]
            )
            cls.session.add(user2)
            cls.session.add(room)
            cls.session.commit()

    def test_delete_the_message(self):
        self.login('user@example.com')

        with cas_mockup_server(), self.given(
            'Try to delete a message',
            '/apiv1/messages/id:1',
            'DELETE'
        ):
            assert status == 200
            assert response.json['body'] == 'This message is deleted'
            assert response.json['removedAt'] is not None

            when(
                'Delete a message with attachment',
                url_parameters=Update(id=self.message3.id)
            )
            assert status == 200
            assert response.json['attachment'] is None

            when('Delete the same message')
            assert status == '616 Message Already Deleted'

            when(
                'Try to delete someone else messages',
                url_parameters=Update(id=self.message2.id)
            )
            assert status == 403

            when('The message not exists', url_parameters=Update(id=0))
            assert status == '614 Message Not Found'

            when(
                'Trying to pass using invalid message id',
                url_parameters=Update(id='Invalid')
            )
            assert status == '707 Invalid MessageId'

            self.logout()
            self.login('user2@example.com')
            when(
                'Not allowed to delete the message',
                url_parameters=Update(id=self.message2.id),
                authorization=self._authentication_token
            )
            assert status == 403

