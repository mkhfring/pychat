from nanohttp import settings
from restfulpy.cli import Launcher, RequireSubCommand
from restfulpy.orm import DBSession

from ..models import Member


class MemberListLauncher(Launcher):  # pragma: no cover

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('list', help='List members.')
        return parser

    def launch(self):
        for m in DBSession.query(Member):
            print(m)


class MemberLauncher(Launcher, RequireSubCommand):  # pragma: no cover

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('member', help="Manage members")
        _subparsers = parser.add_subparsers(
            title="Members managements",
            dest="member_command"
        )
        MemberListLauncher.register(_subparsers)
        return parser

