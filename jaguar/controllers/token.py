import json as json_library

from nanohttp import RestController, json, context, HTTPBadRequest, validate, \
    HTTPForbidden, settings
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit

from ..backends import CASClient
from ..models import Member


class TokenController(RestController):

    @authorize
    @json
    def invalidate(self):
        context.application.__authenticator__.logout()
        return {}

    @json(prevent_form='711 Form Not Allowed')
    def request(self):
        return dict(
            scopes=['email', 'title', 'avatar'],
            applicationId=settings.oauth['application_id'],
        )

    @json
    @commit
    def obtain(self):
        # FIXME: Validation and prevent form.
        cas_server = CASClient()
        access_token, member_id = cas_server \
            .get_access_token(context.form.get('authorizationCode'))

        member = cas_server.get_member(access_token)
        user = DBSession.query(Member) \
            .filter(Member.email == member['email']) \
            .one_or_none()

        if user is None:
            user = Member(
                email=member['email'],
                title=member['title'],
                access_token=access_token,
                reference_id=member['id'],
                avatar=member['avatar'],
            )

        if user.title != member['title']:
            user.title = member['title']

        if user.avatar != member['avatar']:
            user.avatar = member['avatar']

        if user.access_token != access_token:
            user.access_token = access_token

        DBSession.add(user)
        DBSession.flush()
        principal = user.create_jwt_principal()
        context.response_headers.add_header(
            'X-New-JWT-Token',
            principal.dump().decode('utf-8')
        )

        return dict(token=principal.dump().decode('utf-8'))

