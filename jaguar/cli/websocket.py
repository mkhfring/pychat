from aiohttp import web
from restfulpy.cli import Launcher, RequireSubCommand

from ..messaging.websocket import app

DEFAULT_ADDRESS = '8085'


class WebsocketStartLauncher(Launcher): # pragma: no cover
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser(
            'start',
            help='Starts the websocket server.'
        )
        parser.add_argument(
            '-b',
            '--bind',
            default=DEFAULT_ADDRESS,
            metavar='{HOST:}PORT',
            help='Bind Address. default: %s' % DEFAULT_ADDRESS
        )
        return parser

    def launch(self):
        host, port = self.args.bind.split(':')\
            if ':' in self.args.bind else ('', self.args.bind)
        kw = {}
        if port:
            kw['port'] = port

        if host:
            kw['host'] = host

        web.run_app(app, **kw)


class WebsocketLauncher(Launcher, RequireSubCommand):  # pragma: no cover
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('websocket', help='Websocket related.')
        websocket_subparsers = parser.add_subparsers(
            title='Websocket server administration.',
            dest='websocket_command'
        )
        WebsocketStartLauncher.register(websocket_subparsers)
        return parser

