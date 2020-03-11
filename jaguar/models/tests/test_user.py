
import pytest
from nanohttp import HTTPStatus

from jaguar.models.membership import Member
from jaguar.models.target import Room


# Test target model
def test_member_model(db):
    session = db()
    member = Member(
        title='example',
        email='example@example.com',
        access_token='access token',
        reference_id=4
    )
    session.add(member)
    session.commit()
    assert session.query(Member).count() == 1
    assert member.add_to_room == True

    # Testing rooms of a member
    room = Room(title='example')
    session.add(room)
    member.rooms.append(room)
    session.commit()

    # Since the selectin loading is used to load relations,
    # the relation is already load.
    assert member.rooms[0].title == 'example'

    # Testing rooms of an administrator
    member.administrator_of.append(room)
    session.commit()

    assert member.administrator_of[0].title == 'example'
    assert member.administrator_of[0].id == 1

    # Testing relationship between Member and Member ( As contactlist)
    contact = Member(
        title='contact',
        email='contact@example.com',
        access_token='access token',
        reference_id=5
    )
    session.add(contact)
    member.contacts.append(contact)
    session.commit()
    assert len(member.contacts) == 1

    # Testing other side of relationship
    session.commit()
    member.blocked_members.append(contact)
    assert len(member.blocked_members) == 1

