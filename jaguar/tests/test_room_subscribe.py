from bddrest.authoring import response, when, status

from jaguar.models.membership import Member
from jaguar.models.target import Room
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestSubscribeRoom(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        session.add(cls.user1)

        cls.user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token2',
            reference_id=3
        )
        cls.room1 = Room(title='room1', owner=cls.user2)
        session.add(cls.room1)

        cls.room2 = Room(title='room2', owner=cls.user2)
        session.add(cls.room2)

        room3 = Room(title='room3', owner=cls.user2)
        session.add(room3)

        room4 = Room(title='room4', owner=cls.user2)
        session.add(room4)

        room5 = Room(title='room5', owner=cls.user2)
        session.add(room5)

        room6 = Room(title='room6', owner=cls.user2)
        session.add(room6)

        room7 = Room(title='room7', owner=cls.user2)
        session.add(room7)
        session.commit()

    def test_subscribe_rooms(self):
         self.login('user1@example.com')
         rooms = (str(i) + ', ' for i in range(1, 102))
         rooms_string = ''.join(rooms)

         with cas_mockup_server(), self.given(
             'Subscribe multiple rooms',
             f'/apiv1/rooms?id=IN({self.room1.id}, {self.room2.id})',
             'SUBSCRIBE',
         ):
             assert status == 200
             assert len(response.json) == 2
             assert response.json[0]['title'] == 'room1'
             assert response.json[0]['ownerId'] == self.user2.id

             when(
                 'There is form parameter',
                 form=dict(parameter='abc')
             )
             assert status == '711 Form Not Allowed'

             when(
                 'The number of rooms to subscribe is more than limit',
                 query=dict(id=f'IN({rooms_string})')
             )
             assert status == '716 Maximum 5 Rooms To Subscribe At A Time'

             when('Try to pass unauthorize request', authorization=None)
             assert status == 401

