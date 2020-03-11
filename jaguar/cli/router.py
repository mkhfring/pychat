import asyncio

from restfulpy.cli import Launcher, RequireSubCommand
from nanohttp import settings

from ..messaging.router import start as start_router


class RouterStartLauncher(Launcher): # pragma: no cover
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser(
            'start',
            help='Starts the message router.'
        )
        return parser

    def launch(self):
        loop = asyncio.get_event_loop()
        queue = settings.messaging.workers_queue
        print(f'Listenning on: {queue}')
        loop.run_until_complete(start_router(queue))


class RouterLauncher(Launcher, RequireSubCommand):
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('router', help='Message router.')
        router_subparsers = parser.add_subparsers(
            title='Message router',
            dest='router_command'
        )
        RouterStartLauncher.register(router_subparsers)
        return parser


