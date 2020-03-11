
from bddrest.authoring import response, when, Update, Remove, status

from jaguar.models.membership import Member
from jaguar.models.target import Room
from jaguar.tests.helpers import AutoDocumentationBDDTest, cas_mockup_server


class TestListRooms(AutoDocumentationBDDTest):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.user1 = Member(
            email='user1@example.com',
            title='user1',
            access_token='access token1',
            reference_id=2
        )
        cls.user2 = Member(
            email='user2@example.com',
            title='user2',
            access_token='access token2',
            reference_id=3
        )
        room1 = Room(title='room1', owner=cls.user1)
        session.add(room1)
        room2 = Room(title='room2', owner=cls.user1)
        session.add(room2)
        room3 = Room(title='room3', owner=cls.user2)
        session.add(room3)
        session.commit()

    def test_list_rooms_of_user(self):
         self.login('user1@example.com')

         with cas_mockup_server(), self.given(
             'List all the rooms a user owns',
             '/apiv1/rooms',
             'LIST',
         ):
             assert status == 200
             assert len(response.json) == 2
             assert response.json[0]['title'] == 'room1'
             assert response.json[0]['ownerId'] == self.user1.id

             self.logout()
             self.login('user2@example.com')
             when(
                 'List the rooms for another user',
                 authorization=self._authentication_token
             )
             assert status == 200
             assert len(response.json) == 1
             assert response.json[0]['title'] == 'room3'
             assert response.json[0]['ownerId'] == self.user2.id

