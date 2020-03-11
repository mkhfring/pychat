import functools
from os.path import join, dirname

from restfulpy.application import Application
from sqlalchemy_media import StoreManager, FileSystemStore
from nanohttp import settings

from .authentication import Authenticator
from .controllers.root import Root
from .cli import EmailLauncher, MemberLauncher, TargetLauncher, \
    TokenLauncher, WebsocketLauncher, RouterLauncher


__version__ = '0.11.2a3'


class Jaguar(Application):
    __authenticator__ = Authenticator()
    __configuration__ = '''

    db:
      url: postgresql://postgres:postgres@localhost/jaguar_dev
      test_url: postgresql://postgres:postgres@localhost/jaguar_test
      administrative_url: postgresql://postgres:postgres@localhost/postgres

    activation:
      secret: activation-secret
      max_age: 86400  # seconds
      url: http://example.com/activate

    oauth:
      secret: A1dFVpz4w/qyym+HeXKWYmm6Ocj4X5ZNv1JQ7kgHBEk=
      application_id: 1
      url: http://localhost:8083

    storage:
      local_directory: %(root_path)s/data/assets
      base_url: http://localhost:8080/assets

    attachements:
      messages:
        files:
          max_length: 50 # KB
          min_length: 1 # KB

    room:
      subscription:
        max_length: 100

    messaging:
        workers_queue: jaguar_workers
        redis:
            host: localhost
            port: 6379
            password: ~
            db: 1

    webhooks:
      sent:
        url: http://localhost:8081/apiv1/issues
        verb: SENT
        timeout: 0.5 # Seconds
      mentioned:
        url: http://localhost:8081/apiv1/issues
        verb: MENTIONED
        timeout: 0.5 # Seconds

    '''

    def __init__(self, application_name='jaguar', root=Root()):
        super().__init__(
            application_name,
            root=root,
            root_path=join(dirname(__file__), '..'),
            version=__version__,
        )

    def register_cli_launchers(self, subparsers):
        EmailLauncher.register(subparsers)
        WebsocketLauncher.register(subparsers)
        RouterLauncher.register(subparsers)
        MemberLauncher.register(subparsers)
        TargetLauncher.register(subparsers)
        TokenLauncher.register(subparsers)

    def insert_mockup(self):
        from . import mockup
        mockup.insert()


    @classmethod
    def initialize_orm(cls, engine=None):
        StoreManager.register(
            'fs',
            functools.partial(
                FileSystemStore,
                settings.storage.local_directory,
                base_url=settings.storage.base_url,
            ),
            default=True
        )
        super().initialize_orm(cls, engine)


jaguar = Jaguar()

