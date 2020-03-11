import ujson
from nanohttp import settings, HTTPStatus, context
from restfulpy.orm import Field, DeclarativeBase, ModifiedMixin,relationship,\
    ActivationMixin, OrderingMixin, FilteringMixin, PaginationMixin, \
    SoftDeleteMixin, TimestampMixin
from restfulpy.orm.metadata import FieldInfo
from sqlalchemy import Integer, ForeignKey, Unicode, Table, Boolean, JSON, \
    select, bindparam, join
from sqlalchemy.orm import column_property
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy_media import File, MagicAnalyzer, ContentTypeValidator
from sqlalchemy_media.constants import KB
from sqlalchemy_media.exceptions import ContentTypeValidationError, \
    MaximumLengthIsReachedError
from sqlalchemy.ext.hybrid import hybrid_property

from .membership import Member


JSON_MIMETYPE = ['application/x-auditlog']


class MemberMessageSeen(DeclarativeBase, TimestampMixin):
    __tablename__ = 'member_message_seen'

    message_id = Field(Integer, ForeignKey('envelop.id'), primary_key=True)
    member_id = Field(Integer, ForeignKey('member.id'), primary_key=True)


class FileAttachment(File):

    _internal_max_length = None

    _internal_min_length = None

    __pre_processors__ = [
        MagicAnalyzer(),
    ]

    @property
    def __max_length__(self):
        if self._internal_max_length is None:
            self._internal_max_length = \
                settings.attachements.messages.files.max_length * KB

        return self._internal_max_length

    @__max_length__.setter
    def __max_length__(self, v):
        self._internal_max_length = v

    @property
    def __min_length__(self):
        if self._internal_min_length is None:
            self._internal_min_length = \
                settings.attachements.messages.files.min_length * KB

        return self._internal_min_length

    @__min_length__.setter
    def __min_length__(self, v):
        self._internal_min_length = v


class Envelop(OrderingMixin, PaginationMixin, FilteringMixin, ModifiedMixin,
              SoftDeleteMixin, ActivationMixin, DeclarativeBase):
    __tablename__ = 'envelop'

    id = Field(Integer, primary_key=True)
    type = Field(Unicode(25))
    target_id = Field(Integer, ForeignKey('target.id'))
    sender_id = Field(Integer, ForeignKey('member.id'))
    body = Field(
        Unicode(65536),
        required=True,
        not_none=True,
        min_length=1,
        protected=False,
        python_type=str,
        watermark='Loerm Ipsum',
        example='Loerm Ipsum',
        message='Loerm Ipsum',
        label='Text or caption',
    )

    sender_reference_id = column_property(
        select([Member.reference_id]) \
        .where(Member.id == sender_id) \
        .correlate_except(Member),
        deferred=True
    )

    def to_dict(self):
        envelop_dictionary = super().to_dict()
        envelop_dictionary.update(
            senderReferenceId=self.sender_reference_id
        )
        return envelop_dictionary

    @classmethod
    def json_metadata(cls):
        metadata = super().json_metadata()
        metadata['fields']['senderReferenceId'] = FieldInfo(
            Integer,
            not_none=True,
            readonly=True,
            required=False,
        ).to_json()
        return metadata

    __mapper_args__ = {
        'polymorphic_identity': __tablename__,
        'polymorphic_on': type,
    }


is_mine_fieldinfo = FieldInfo(Boolean, not_none=True, readonly=True)


class Message(Envelop):

    __mapper_args__ = {'polymorphic_identity': 'message'}
    __exclude__ = {'seen_by'}

    mimetype = Field(
        Unicode(25),
        required=False,
        python_type=str,
        nullable=True,
        protected=False,
        not_none=False,
        watermark='Loerm Ipsum',
        example='plain/text',
        message='Loerm Ipsum',
        label='File type',
    )

    # A message can be a reply to another message, so The id of
    # the source message is set in reply_root
    reply_root = Field(Integer, ForeignKey('envelop.id'), nullable=True)

    _attachment = Field(
        FileAttachment.as_mutable(JSON),
        nullable=True,
        protected=False,
        json='attachment'
    )

    @property
    def attachment(self):
        return self._attachment if self._attachment else None

    @attachment.setter
    def attachment(self, value):
        if value is not None:
            try:
                self._attachment = FileAttachment.create_from(value)

            except ContentTypeValidationError:
                raise HTTPStatus(
                    '710 The Mimetype Does Not Match The File Type'
                )

            except MaximumLengthIsReachedError:
                raise HTTPStatus('413 Request Entity Too Large')

        else:
            self._attachment = None


    # Since this relationship should be a many to one relationship,
    # The remote_side is declared
    reply_to = relationship(
        'Message',
        remote_side=[Envelop.id],
        protected=False
    )

    # Since collections would be fairly small,
    # selecin loding is chosen for this relationship.
    seen_by = relationship(
        'Member',
        protected=True,
        secondary='member_message_seen',
        lazy='selectin'
    )

    seen_at = column_property(
        select([MemberMessageSeen.created_at]) \
        .select_from(
            join(
                Member,
                MemberMessageSeen,
                MemberMessageSeen.member_id == Member.id
            )
        ) \
        .where(MemberMessageSeen.message_id == Envelop.id) \
        .where(Member.reference_id == bindparam(
            'reference_id',
            callable_=lambda: context.identity.reference_id
        )) \
        .correlate_except(MemberMessageSeen),
        deferred=True
    )

    @hybrid_property
    def is_mine(self):
        return Member.current().reference_id == self.sender_reference_id

    @is_mine.expression
    def is_mine(cls):
        return cls.sender_reference_id == bindparam(
            'reference_id',
            callable_=lambda: context.identity.reference_id
        )

    def to_dict(self):
        seen_by_list = []
        for member in self.seen_by:
            seen_by_list.append({
                'id': member.id,
                'referenceId': member.reference_id,
                'email': member.email,
                'title': member.title,
                'avatar': member.avatar,
                'phone': member.phone,
            })

        message_dictionary = super().to_dict()
        message_dictionary.update(
            isMine=self.is_mine,
            activatedAt=self.activated_at,
            attachment=self.attachment.locate() \
                if self.attachment and not self.is_deleted else None,
            body=ujson.loads(self.body) \
                if self.mimetype in JSON_MIMETYPE else self.body,
            seenBy=seen_by_list,
        )
        return message_dictionary

    @classmethod
    def json_metadata(cls):
        metadata = super().json_metadata()
        metadata['fields']['isMine'] = is_mine_fieldinfo.to_json()
        return metadata

    # TODO: Remove these redundant lines.
    __mapper_args__ = {
        'polymorphic_identity' : 'message',
    }

