import sys

from restfulpy.orm import DBSession
from restfulpy.cli import Launcher, RequireSubCommand

from ..models import Member


class CreateTokenLauncher(Launcher):
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser(
            'create',
            help='Creates a jwt token.'
        )
        parser.add_argument(
            'member_id',
            type=int,
            help='Member id'
        )
        parser.add_argument(
            'access_token',
            type=str,
            help='Access token'
        )
        return parser

    def launch(self):
        member = DBSession.query(Member)\
            .filter(Member.id == self.args.member_id)\
            .one_or_none()

        if member is None:
            print(f'Invalid member id: {self.args.member_id}', file=sys.stderr)
            return 1

        member.access_token = self.args.access_token
        DBSession.commit()

        token = member.create_jwt_principal()
        print(token.dump().decode())


class TokenLauncher(Launcher, RequireSubCommand):

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('token', help="Token related.")
        _subparsers = parser.add_subparsers(
            title="Token",
            dest="token_command"
        )
        CreateTokenLauncher.register(_subparsers)
        return parser

