
from jaguar.models.target import Room
from jaguar.models.membership import Member


def test_target_model(db):
    session = db()
    room = Room(title='example', type='room')
    session.add(room)
    session.commit()
    assert session.query(Room).count() == 1

    # Test members of a room
    member = Member(
        title='example',
        email='example@example.com',
        access_token='access token',
        reference_id=2
    )
    session.add(member)
    room.members.append(member)
    room.owner = member
    session.commit()
    # Since the selectin loading is used to load relations,
    # the relation is already load.
    assert room.members[0].title == 'example'

    # Test administrators of a room
    administrator = Member(
        title='administrator',
        email='administrator@example.com',
        access_token='access token',
        reference_id=3
    )
    session.add(administrator)
    session.commit()
    room.administrators.append(administrator)
    session.commit()
    assert room.administrators[0].title == 'administrator'
    assert room.owner_id == 1
