from sqlalchemy import and_, or_
from nanohttp import json, context, HTTPStatus, HTTPNotFound, settings
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import Target, Room, member_block, Member, TargetMember
from ..validators import create_room_validator, kick_member_validator


class RoomController(ModelRestController):
    __model__ = Target

    @authorize
    @json
    @Room.expose
    @commit
    @create_room_validator
    def create(self):
        title = context.form.get('title')
        current_user = DBSession.query(Member) \
            .filter(Member.reference_id == context.identity.reference_id) \
            .one()
        is_exist = DBSession.query(Room) \
            .filter(
                Room.title == title, Room.owner_id == current_user.id
            ) \
            .count()
        if  is_exist:
            raise HTTPStatus('615 Room Already Exists')

        room = Room(title=title)
        member = Member.current()
        room.administrators.append(member)
        room.members.append(member)

        room.owner = member
        DBSession.add(room)
        return room

    @json
    @Room.expose
    @commit
    def add(self, id: int):
        user_id = context.form.get('userId')
        requested_user = DBSession.query(Member) \
            .filter(Member.reference_id == user_id) \
            .one_or_none()
        if requested_user is None:
            raise HTTPStatus('611 Member Not Found')

        room = DBSession.query(Room).filter(Room.id == id).one_or_none()
        if room is None:
            raise HTTPStatus('612 Room Not Found')

        is_member = DBSession.query(TargetMember) \
            .filter(
                TargetMember.target_id == id,
                TargetMember.member_id == requested_user.id
            ) \
            .count()
        if is_member:
            raise HTTPStatus('604 Already Added To Target')

        if not requested_user.add_to_room:
            raise HTTPStatus('602 Not Allowed To Add This Person To Any Room')

        current_user = DBSession.query(Member) \
            .filter(Member.reference_id == context.identity.reference_id) \
            .one()
        is_blocked = DBSession.query(member_block) \
            .filter(or_(
                and_(
                    member_block.c.member_id == requested_user.id,
                    member_block.c.blocked_member_id == current_user.id
                ),
                and_(
                    member_block.c.member_id == current_user.id,
                    member_block.c.blocked_member_id == requested_user.id
                )
            )) \
            .count()
        if is_blocked:
            raise HTTPStatus('601 Not Allowed To Add Member To Any Room')

        room.members.append(requested_user)
        return room

    @authorize
    @json
    @Target.expose
    def list(self):
        current_user = DBSession.query(Member) \
            .filter(Member.reference_id == context.identity.reference_id) \
            .one()
        query = DBSession.query(Room)
        if not context.identity.is_in_roles('admin'):
            query =  query.filter(
                Room.owner_id == current_user.id
            )

        return query

    @authorize
    @kick_member_validator
    @json
    @Room.expose
    @commit
    def kick(self, id):
        try:
            id = int(id)
        except(ValueError, TypeError):
            raise HTTPNotFound()

        room = DBSession.query(Room).filter(Room.id == id).one_or_none()
        if room is None:
            raise HTTPNotFound()

        member_id = context.form.get('memberId')
        member = DBSession.query(Member) \
            .filter(Member.reference_id == member_id).one_or_none()
        if member is None:
            raise HTTPStatus('611 Member Not Found')

        is_member = DBSession.query(Member) \
            .filter(
                TargetMember.target_id == id,
                TargetMember.member_id == member.id
            ) \
            .count()
        if not is_member:
            raise HTTPStatus('617 Not A Member')

        DBSession.query(TargetMember) \
            .filter(
                TargetMember.target_id == id,
                TargetMember.member_id == member.id
            ) \
            .delete()
        return room


    @authorize
    @json(prevent_form='711 Form Not Allowed')
    @Room.expose
    @commit
    def subscribe(self):
        member = Member.current()
        query = DBSession.query(Room)
        requested_rooms = Target.filter_by_request(query).all()

        if len(requested_rooms) >= settings.room.subscription.max_length:
            raise HTTPStatus(
                f'716 Maximum {settings.room.subscription.max_length} Rooms '
                f'To Subscribe At A Time'
            )

        requested_rooms_id = {i.id for i in requested_rooms}

        subscribed_rooms = DBSession.query(TargetMember) \
            .filter(TargetMember.member_id == member.id) \
            .join(Target, Target.id == TargetMember.target_id) \
            .filter(Target.type == 'room') \
            .all()
        subscribed_rooms_id = {i.target_id for i in subscribed_rooms}
        not_subscribed_rooms_id = requested_rooms_id - subscribed_rooms_id

        flush_counter = 0
        for each_room_id in not_subscribed_rooms_id:
            flush_counter += 1
            target_member = TargetMember(
                target_id=each_room_id,
                member_id=member.id
            )
            DBSession.add(target_member)
            if flush_counter % 10 == 0:
                DBSession.flush()

        not_subscribed_rooms = DBSession.query(Target) \
            .filter(Target.id.in_(not_subscribed_rooms_id))
        return not_subscribed_rooms

