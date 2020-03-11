from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Envelop


class EnvelopController(ModelRestController):
    __model__ = Envelop

    @authorize
    @json
    @Envelop.expose
    def list(self):
        return DBSession.query(Envelop)

