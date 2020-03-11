from sqlalchemy import Integer
from restfulpy.orm import Field

from .envelop import Envelop


class Mention(Envelop):

    __mapper_args__ = {'polymorphic_identity': 'mention'}

    origin_target_id = Field(
        Integer,
        python_type=int,
        minimum=1,
        nullable=True,
        required=True,
        not_none=False,
        watermark='Lorem Ipsum',
        example='Lorem Ipsum',
        message='Lorem Ipsum',
        label='Origin target',
    )

