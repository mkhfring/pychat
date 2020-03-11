import uuid

from cas import CASPrincipal
from nanohttp import context
from restfulpy.orm import DeclarativeBase, Field, ModifiedMixin, \
    ActivationMixin, SoftDeleteMixin, relationship, DBSession, \
    FilteringMixin, PaginationMixin, OrderingMixin
from restfulpy.principal import JwtRefreshToken
from sqlalchemy import Unicode, Integer, ForeignKey, Boolean, Table


member_block = Table(
    'blocked',
    DeclarativeBase.metadata,
    Field(
        'member_id',
        Integer,
        ForeignKey('member.id'),
        primary_key=True,
    ),
    Field(
        'blocked_member_id',
        Integer,
        ForeignKey('member.id'),
        primary_key=True
    )
)


class MemberContact(DeclarativeBase):
    __tablename__ = 'member_contact'

    member_id = Field(Integer, ForeignKey('member.id'), primary_key=True)
    contact_member_id = Field(Integer, ForeignKey('member.id'), primary_key=True)


class TargetMember(DeclarativeBase):
    __tablename__ = 'target_member'

    target_id = Field(Integer, ForeignKey('target.id'), primary_key=True)
    member_id = Field(Integer, ForeignKey('member.id'), primary_key=True)


class Member(OrderingMixin, FilteringMixin, PaginationMixin, DeclarativeBase):
    __tablename__ = 'member'

    id = Field(Integer, primary_key=True)
    reference_id = Field(Integer, unique=True)
    email = Field(
        Unicode(100),
        unique=True,
        index=True,
        not_none=False,
        required=True,
        min_length=7,
        max_length=100,
        message='Loerm Ipsum',
        label='Email address',
        example='user@example.com',
        watermark='user@example.com',
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
        pattern_description='Valid email format, example: user@example.com',
    )
    access_token = Field(Unicode(512), protected=True)

    # FIXME: What is this?
    add_to_room = Field(Boolean, default=True)
    title = Field(
        Unicode(50),
        unique=True,
        index=True,
        nullable=True,
        max_length=20,
        min_length=3,
        label='Username',
        required=True,
        message='Loerm Ipsum',
        not_none=True,
        watermark='John_Doe',
        example='John_Doe',
    )
    phone = Field(
        Unicode(50),
        nullable=True,
        min_length=8,
        max_length=16,
        not_none=False,
        required=False,
        message='Loerm Ipsum',
        label='Phone',
        watermark='Enter your phone number',
        example='734 555 1212',
        pattern=r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}'
            r'[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}',
    )
    show_email = Field(Boolean, default=False)
    show_phone = Field(Boolean, default=False)
    avatar = Field(
        Unicode(200),
        label='Avatar',
        nullable=True,
        unique=False,
        not_none=False,
        required=False,
        example='Lorem Ipsum'
    )

    messages = relationship('Envelop')
    contacts = relationship(
        'Member',
        secondary='member_contact',
        primaryjoin=id == MemberContact.member_id,
        secondaryjoin=id == MemberContact.contact_member_id,
        lazy='selectin'
    )
    room = relationship('Room', back_populates='owner')
    blocked_members = relationship( 'Member',
        secondary=member_block,
        primaryjoin=id == member_block.c.member_id,
        secondaryjoin=id == member_block.c.blocked_member_id,
        lazy='selectin'
    )

    def create_jwt_principal(self, session_id=None):
        if session_id is None:
            session_id = str(uuid.uuid4())

        return CASPrincipal(dict(
            id=self.id,
            roles=self.roles,
            email=self.email,
            name=self.title,
            referenceId=self.reference_id,
            sessionId=session_id,
            avatar=self.avatar,
        ))

    def create_refresh_principal(self):
        return JwtRefreshToken(dict(
            id=self.id
        ))

    @classmethod
    def current(cls):
        return DBSession.query(cls) \
            .filter(cls.reference_id == context.identity.reference_id).one()

    def is_member(self, target_id):
        return DBSession.query(Member).join(TargetMember) \
            .filter(
                TargetMember.target_id == target_id,
                TargetMember.member_id == self.id
            ) \
            .count()

    def to_dict(self):
        member_dict = super().to_dict()
        member_dict['phone'] = self.phone if self.show_phone else None
        member_dict['email'] = self.email if self.show_email else None
        return member_dict

    @property
    def roles(self):
        return ['member']

    def __repr__(self):
        return f'Member: {self.id} {self.reference_id} {self.title} {self.email}'

