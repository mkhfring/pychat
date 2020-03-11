from nanohttp import settings
from restfulpy.cli import Launcher, RequireSubCommand
from restfulpy.orm import DBSession

from ..models import Target


class TargetListLauncher(Launcher):  # pragma: no cover

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('list', help='List targets.')
        return parser

    def launch(self):
        for m in DBSession.query(Target):
            print(m)


class TargetLauncher(Launcher, RequireSubCommand):  # pragma: no cover

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('target', help="Manage targets")
        _subparsers = parser.add_subparsers(
            title="Targets managements",
            dest="target_command"
        )
        TargetListLauncher.register(_subparsers)
        return parser

