
from nanohttp import json, context, HTTPUnauthorized, HTTPStatus, \
    HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Target, Room, TargetMember, Member
from .message import MessageController
from .mention import MentionController
from .member import MemberController


class TargetController(ModelRestController):
    __model__ = Target

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1 and remaining_paths[1] == 'messages':
            target = self._get_target(remaining_paths[0])
            return MessageController()(remaining_paths[0], *remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'mentions':
            target = self._get_target(remaining_paths[0])
            return MentionController(target=target)(*remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'members':
            id = int_or_notfound(remaining_paths[0])
            target = self._get_target(remaining_paths[0])
            return TargetMemberController(target=target)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def _get_target(self, id):
        try:
            int(id)
        except:
            raise HTTPStatus('706 Invalid Target Id')
        target = DBSession.query(Target).filter(Target.id == id).one_or_none()
        if target is None:
            raise HTTPNotFound('Target Not Exists')

        return target


class TargetMemberController(ModelRestController):
    __model__ = Member

    def __init__(self, target):
        self.target = target

    @authorize
    @json(prevent_form='711 Form Not Allowed')
    @Member.expose
    def list(self):
        query = DBSession.query(Member) \
            .join(TargetMember, TargetMember.member_id == Member.id) \
            .filter(TargetMember.target_id == self.target.id)
        return query

