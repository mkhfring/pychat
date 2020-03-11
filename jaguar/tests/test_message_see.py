import io
from os.path import abspath, join, dirname
import ujson

from nanohttp.contexts import Context
from nanohttp import context
from bddrest.authoring import when, status, response
from sqlalchemy_media import StoreManager

from jaguar.models import Member, Room, Message, MemberMessageSeen
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


THIS_DIR = abspath(join(dirname(__file__)))
IMAGE_PATH = join(THIS_DIR, 'stuff', '150x150.png')


class TestSeeMessage(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        with StoreManager(session):
            with open(IMAGE_PATH, 'rb') as f:
                cls.user1 = Member(
                    email='user@example.com',
                    title='user',
                    access_token='access token',
                    reference_id=1,
                )
                session.add(cls.user1)

                cls.user2 = Member(
                    email='user2@example.com',
                    title='user2',
                    access_token='access token2',
                    reference_id=2,
                )
                session.add(cls.user2)

                room = Room(
                    title='room',
                    type='room',
                    members=[cls.user1, cls.user2]
                )
                session.add(room)
                session.flush()

                auditlog_message1 = Message(
                    body='{"log": 1}',
                    mimetype='application/x-auditlog',
                    target_id=room.id,
                    sender_id=cls.user2.id,
                )
                session.add(auditlog_message1)

                auditlog_message2 = Message(
                    body='{"log": 1}',
                    mimetype='application/x-auditlog',
                    target_id=room.id,
                    sender_id=cls.user2.id,
                )
                session.add(auditlog_message2)

                auditlog_message3 = Message(
                    body='{"log": 1}',
                    mimetype='application/x-auditlog',
                    target_id=room.id,
                    sender_id=cls.user2.id,
                )
                session.add(auditlog_message3)

                cls.message1 = Message(
                    body='This is message 1',
                    mimetype='text/plain',
                    target_id=room.id,
                    sender_id=cls.user1.id,
                )
                session.add(cls.message1)

                cls.message2 = Message(
                    body='This is message 2',
                    mimetype='text/plain',
                    target_id=room.id,
                    sender_id=cls.user1.id
                )
                session.add(cls.message2)

                cls.message3 = Message(
                    body='This is message 3',
                    mimetype='text/plain',
                    target_id=room.id,
                    sender_id=cls.user2.id,
                    attachment=io.BytesIO(f.read()),
                )
                session.add(cls.message3)
                session.flush()

                cls.message4 = Message(
                    body='This is message 4',
                    mimetype='text/plain',
                    target_id=room.id,
                    sender_id=cls.user2.id,
                )
                session.add(cls.message3)

                member_message_seen1 = MemberMessageSeen(
                    member_id=cls.user1.id,
                    message_id=cls.message1.id
                )
                session.add(member_message_seen1)

                member_message_seen2 = MemberMessageSeen(
                    member_id=cls.user1.id,
                    message_id=cls.message2.id
                )
                session.add(member_message_seen2)
                session.commit()

                cls.auditlog_message1_id = auditlog_message1.id
                cls.auditlog_message2_id = auditlog_message2.id
                cls.auditlog_message3_id = auditlog_message3.id

    def test_see_message(self):
        class Identity:
            def __init__(self, user):
                self.id = user.id
                self.reference_id = user.reference_id

        self.login(self.user1.email)

        with Context(dict()), cas_mockup_server(), self.given(
            f'See a message',
            f'/apiv1/messages/id:{self.message3.id}',
            f'SEE',
            query=dict(mimetype='!application/x-auditlog')
        ):
            assert status == 200
            assert response.json['id'] == self.message3.id
            assert response.json['body'] == self.message3.body
            assert response.json['seenAt'] is not None
            assert response.json['attachment'] is not None
            assert response.json['modifiedAt'] is None
            assert response.json['seenBy'][0]['id'] is not None
            assert response.json['seenBy'][0]['referenceId'] is not None
            assert response.json['seenBy'][0]['title'] is not None
            assert response.json['seenBy'][0]['avatar'] is not None
            assert response.json['seenBy'][0]['email'] is not None
            assert response.json['seenBy'][0]['phone'] is None

            context.identity = Identity(self.user1)
            session = self.create_session()
            auditlog_message1 = session.query(Message) \
                .get(self.auditlog_message1_id)
            auditlog_message2 = session.query(Message) \
                .get(self.auditlog_message2_id)
            auditlog_message3 = session.query(Message) \
                .get(self.auditlog_message3_id)

            assert auditlog_message1.seen_at is None
            assert auditlog_message2.seen_at is None
            assert auditlog_message3.seen_at is None

            message1 = session.query(Message).get(self.message1.id)
            message2 = session.query(Message).get(self.message2.id)
            message3 = session.query(Message).get(self.message3.id)

            assert message1.seen_at is not None
            assert message2.seen_at is not None
            assert message3.seen_at is not None

            when(
                'See an auditlog message',
                url_parameters=dict(id=self.auditlog_message2_id),
                query=dict(mimetype='application/x-auditlog'),
            )
            assert status == 200

            session = self.create_session()
            auditlog_message1 = session.query(Message) \
                .get(self.auditlog_message1_id)
            auditlog_message2 = session.query(Message) \
                .get(self.auditlog_message2_id)
            auditlog_message3 = session.query(Message) \
                .get(self.auditlog_message3_id)

            assert auditlog_message1.seen_at is not None
            assert auditlog_message2.seen_at is not None
            assert auditlog_message3.seen_at is None

            when(
                'Sender wants to see own message',
                url_parameters=dict(id=self.message1.id)
            )
            assert status == '621 Can Not See Own Message'

            when('Trying to pass with message already seen')
            assert status == '619 Message Already Seen'

            when('Message is not found', url_parameters=dict(id=0))
            assert status == 404

            when(
                'Message is not found with alphabetical id',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when('Try to pass unauthorize request', authorization=None)
            assert status == 401

