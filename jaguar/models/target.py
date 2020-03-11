from nanohttp import settings
from restfulpy.orm import Field, DeclarativeBase, ModifiedMixin, \
    relationship, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.taskqueue import RestfulpyTask
from sqlalchemy import Integer, ForeignKey, Unicode, BigInteger, Table, \
    UniqueConstraint

from .membership import Member
from .envelop import Envelop


room_administrator = Table(
    'room_administrator',
    DeclarativeBase.metadata,
    Field('room_id', Integer, ForeignKey('target.id')),
    Field('member_id', Integer, ForeignKey('member.id'))
)


class Target(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
             DeclarativeBase):
    __tablename__ = 'target'

    id = Field(Integer, primary_key=True)
    type = Field(
        Unicode(25),
        python_type=str,
        min_length=4,
        not_none=False,
        required=False,
        watermark='Loerm Ipsum',
        message='Loerm Ipsum',
        example='direct',
    )

    # since the number of collections are small, the selectin strategy is
    # more efficient for loading
    members = relationship(
        'Member',
        secondary='target_member',
        backref='rooms',
        lazy='selectin',
        protected=True,
    )
    envelop_id = relationship('Envelop')

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type,
    }


class Room(Target):

    owner_id = Field(Integer, ForeignKey('member.id'), nullable=True)
    owner = relationship('Member', back_populates='room')
    title = Field(
        Unicode(50),
        nullable=True,
        json='title',
        required=True,
        not_none=False,
        python_type=str
    )

    # since the number of collections are small, the selectin strategy is
    # more efficient for loading
    administrators = relationship(
        'Member',
        secondary=room_administrator,
        backref='administrator_of',
        protected=True,
        lazy='selectin'
    )
    UniqueConstraint(owner_id, title, name='unique_room')

    def to_dict(self):
        result = super().to_dict()
        result.update(
            memberIds=[member.id for member in self.members],
            administratorIds= \
                [administrator.id for administrator in self.administrators],
        )
        return result

    messages = relationship('Envelop')
    __mapper_args__ = {
        'polymorphic_identity': 'room',
    }

    def __repr__(self):
        return f'Room: {self.id} {self.title}'


class Direct(Target):

    __mapper_args__ = {
        'polymorphic_identity': 'direct',
    }

    def __repr__(self):
        return f'Direct: {self.id}'

