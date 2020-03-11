import itsdangerous
from nanohttp import settings
from restfulpy.cli import Launcher, RequireSubCommand

from jaguar.models import ActivationEmail


class SendEmailLauncher(Launcher):  # pragma: no cover
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('send', help='Sends an email.')
        parser.add_argument(
            '-e',
            '--email',
            required=True,
            help='Email to be claim'
        )
        return parser

    def launch(self):

        serializer = \
            itsdangerous.URLSafeTimedSerializer(settings.activation.secret)

        token = serializer.dumps(self.args.email)

        email = ActivationEmail(
                to=self.args.email,
                subject='Activate your Cucumber account',
                body={
                    'activation_token': token,
                    'activation_url': settings.activation.url
                }
        )
        email.to = self.args.email
        email.do_({})


class EmailLauncher(Launcher, RequireSubCommand):  # pragma: no cover
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('email', help="Manage emails")
        user_subparsers = parser.add_subparsers(
            title="Email managements",
            dest="email_command"
        )
        SendEmailLauncher.register(user_subparsers)
        return parser
