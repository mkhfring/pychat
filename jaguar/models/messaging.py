
from restfulpy.messaging.models import Email


class ActivationEmail(Email):
    __mapper_args__ = {
        'polymorphic_identity': 'activation_email'
    }
    template_filename = 'activation.mako'

