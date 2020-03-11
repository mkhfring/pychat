
from nanohttp import json, context, validate, HTTPStatus
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import Member, MemberContact
from ..validators import add_contact_validator


class ContactController(ModelRestController):
    __model__ = Member

    @authorize
    @add_contact_validator
    @json
    @Member.expose
    @commit
    def add(self):
        user_id = context.form.get('userId')
        destination = DBSession.query(Member) \
            .filter(Member.id == user_id) \
            .one_or_none()
        if destination is None:
            raise HTTPStatus('611 Member Not Found')

        current_member = DBSession.query(Member) \
            .filter(Member.reference_id == context.identity.reference_id) \
            .one()
        is_contact = DBSession.query(MemberContact) \
            .filter(
                MemberContact.member_id == current_member.id,
                MemberContact.contact_member_id == user_id
            ) \
            .count()
        if is_contact:
            raise HTTPStatus('603 Already Added To Contacts')

        DBSession.add(MemberContact(
            member_id=current_member.id,
            contact_member_id=user_id
        ))
        return destination

    @authorize
    @json
    @Member.expose
    def list(self):
        current_member = DBSession.query(Member) \
            .filter(Member.reference_id == context.identity.reference_id) \
            .one()
        query = DBSession.query(Member) \
            .filter(
                MemberContact.member_id == current_member.id,
                MemberContact.contact_member_id == Member.id
            )
        return query

