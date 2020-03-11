import re

import itsdangerous
from nanohttp import json, context, HTTPBadRequest, HTTPStatus, settings
from restfulpy.controllers import RestController
from restfulpy.orm import commit, DBSession

from ..models import Member, ActivationEmail


class EmailController(RestController):

    @json
    @commit
    def claim(self):
        email = context.form.get('email')
        email_pattern = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        if not email:
            raise HTTPBadRequest()

        if not re.match(email_pattern, email):
            raise HTTPStatus('701 Invalid email format.')

        if DBSession.query(Member.email).filter(Member.email == email).count():
            raise HTTPStatus(
                '601 The requested email address is already registered.'
            )

        # FIXME: Token should be put in payload
        serializer = \
            itsdangerous.URLSafeTimedSerializer(settings.activation.secret)
        token = serializer.dumps(email)
        DBSession.add(
            ActivationEmail(
                to=email,
                subject='Activate your NueMD Coder account',
                body={
                    'activation_token': token,
                    'activation_url': settings.activation.url
                }
            )
        )
        return dict(email=email)

