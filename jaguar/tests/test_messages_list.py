from os.path import abspath, join, dirname

from bddrest.authoring import when, Update, status, response

from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server
from jaguar.models import Room, Member, Message
from sqlalchemy_media import StoreManager


this_dir = abspath(join(dirname(__file__)))
image_path = join(this_dir, 'stuff', '150x150.png')


class TestListMessages(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        with StoreManager(session):
            cls.message1 = Message(
                body='This is message 1',
                mimetype='text/plain',
            )
            cls.message2 = Message(
                body='This is message 2',
                mimetype='text/plain',
            )
            cls.message3 = Message(
                body='This is message 3',
                mimetype='text/plain',
            )
            cls.message4 = Message(
                body='This is message 4',
                mimetype='text/plain',
            )
            cls.message5 = Message(
                body='This is message 5',
                mimetype='image/png',
                attachment=image_path
            )
            cls.message6 = Message(
                body='This is message 6',
                mimetype='text/plain',
            )
            user1 = Member(
                email='user1@example.com',
                title='user',
                access_token='access token1',
                reference_id=2,
                messages=[
                    cls.message1,
                    cls.message2,
                    cls.message3,
                    cls.message5
                ]
            )
            user2 = Member(
                email='user2@example.com',
                title='user2',
                access_token='access token2',
                reference_id=3,
                messages=[cls.message4, cls.message6]
            )
            session.add(user2)
            user3 = Member(
                email='user3@example.com',
                title='user3',
                access_token='access token3',
                reference_id=4,
            )
            room1 = Room(
                title='room1',
                type='room',
                members=[user1, user3],
                messages=[
                    cls.message1,
                    cls.message3,
                    cls.message4,
                    cls.message5,
                    cls.message6
                ]
            )
            session.add(room1)
            room2 = Room(
                title='room2',
                type='room',
                members=[user1, user3],
                messages=[cls.message2],
            )
            session.add(room2)
            session.commit()

    def test_list_messages_of_target(self):
        self.login('user1@example.com')

        with cas_mockup_server(), self.given(
            'List messages of a target',
            '/apiv1/targets/id:1/messages',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 5
            assert response.json[0]['body'] == self.message4.body
            assert response.json[0]['isMine'] is False

            assert response.json[2]['body'] == self.message1.body
            assert response.json[2]['isMine'] is True

            when(
                'Try to send form in the request',
                form=dict(parameter='parameter')
            )
            assert status == '711 Form Not Allowed'

            when('Try to sort the response', query=dict(sort='id'))
            assert len(response.json) == 5
            assert response.json[0]['id'] == 1

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] == 5

            when('Testing pagination', query=dict(take=1, skip=1))
            assert len(response.json) == 1
            assert response.json[0]['body'] == self.message6.body

            when(
                'Sorting befor pagination',
                query=dict(sort='-id', take=2, skip=1)
            )
            assert len(response.json) == 2
            assert response.json[0]['id'] == 4

            when('Filtering the response', query=dict(id=self.message1.id))
            assert len(response.json) == 1
            assert response.json[0]['body'] == self.message1.body

            when(
                'Filtering message by isMine',
                query=dict(isMine='true')
            )
            assert status == 200
            assert len(response.json) == 3
            assert response.json[0]['body'] == 'This is message 1'

            when('Try to pass an Unauthorized request', authorization=None)
            assert status == 401

