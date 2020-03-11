from restfulpy.authorization import authorize
from restfulpy.orm import commit, DBSession
from restfulpy.controllers import ModelRestController
from sqlalchemy_media import store_manager
from nanohttp import json, context, HTTPStatus, validate, HTTPForbidden, \
    settings, HTTPNotFound, int_or_notfound

from ..messaging import queues
from ..models import Envelop, Message, TargetMember, Member, Target, \
    MemberMessageSeen
from ..validators import send_message_validator, edit_message_validator, \
    reply_message_validator
from ..exceptions import HTTPUnsupportedMediaType
from ..webhooks import Webhook


BLACKLIST_MIME_TYPES = ['application/x-dosexec']
SUPPORTED_TEXT_MIME_TYPES = ['text/plain', 'application/x-auditlog']


class MessageController(ModelRestController):
    __model__ = Message

    @store_manager(DBSession)
    @authorize
    @send_message_validator
    @json
    @Message.expose
    @commit
    def send(self, target_id):
        mimetype = context.form.get('mimetype')
        sender = Member.current()
        message = Message(body=context.form.get('body'))
        message.target_id = int(target_id)
        message.sender_id = sender.id

        if 'attachment' in context.form:
            message.attachment = context.form.get('attachment')
            message.mimetype = message.attachment.content_type

            if message.attachment.content_type in BLACKLIST_MIME_TYPES:
                raise HTTPUnsupportedMediaType()

        elif mimetype:
            if mimetype not in SUPPORTED_TEXT_MIME_TYPES:
                raise HTTPUnsupportedMediaType()

            message.mimetype = context.form.get('mimetype')

        else:
            message.mimetype = 'text/plain'

        DBSession.add(message)
        DBSession.flush()
        queues.push(settings.messaging.workers_queue, message.to_dict())
        webhook = Webhook()
        webhook.sent_message(target_id, sender.reference_id)
        return message

    @authorize
    @store_manager(DBSession)
    @json(prevent_form='711 Form Not Allowed')
    @Message.expose
    def list(self, target_id):
        query = DBSession.query(Message) \
            .filter(Message.target_id == target_id)
        return query

    @authorize
    @store_manager(DBSession)
    @json
    @Message.expose
    @commit
    def delete(self, id):
        try:
            id = int(id)
        except:
            raise HTTPStatus('707 Invalid MessageId')

        message = DBSession.query(Message) \
            .filter(Message.id == id) \
            .one_or_none()
        if message is None:
            raise HTTPStatus('614 Message Not Found')

        if message.is_deleted:
            raise HTTPStatus('616 Message Already Deleted')

        if not message.sender_id == Member.current().id:
            raise HTTPForbidden()

        message.body = 'This message is deleted'
        message.mimetype = 'text/plain'
        message.soft_delete()
        DBSession.flush()
        queues.push(settings.messaging.workers_queue, message.to_dict())
        return message

    @authorize
    @store_manager(DBSession)
    @edit_message_validator
    @json
    @Message.expose
    @commit
    def edit(self, id):
        id = int_or_notfound(id)
        new_message_body = context.form.get('body')

        message = DBSession.query(Message).get(id)
        if message is None:
            raise HTTPNotFound()

        if message.is_deleted:
            raise HTTPStatus('616 Message Already Deleted')

        if message.sender_id != Member.current().id:
            raise HTTPForbidden()

        message.body = new_message_body
        DBSession.add(message)
        DBSession.flush()
        queues.push(settings.messaging.workers_queue, message.to_dict())
        return message

    @authorize
    @store_manager(DBSession)
    @json
    @Message.expose
    def get(self, id):
        id = int_or_notfound(id)

        message = DBSession.query(Message).get(id)
        if message is None:
            raise HTTPNotFound()

        return message

    @store_manager(DBSession)
    @authorize
    @reply_message_validator
    @json
    @Message.expose
    @commit
    def reply(self, message_id):
        id = int_or_notfound(message_id)
        mimetype = context.form.get('mimetype')

        requested_message = DBSession.query(Message).get(id)
        if requested_message is None:
            raise HTTPNotFound()

        if requested_message.is_deleted:
            raise HTTPStatus('616 Message Already Deleted')

        message = Message(
            body=context.form.get('body'),
            target_id = requested_message.target_id,
            sender_id = Member.current().id,
            reply_to = requested_message,
        )

        if 'attachment' in context.form:
            message.attachment = context.form.get('attachment')
            message.mimetype = message.attachment.content_type

            if message.attachment.content_type in BLACKLIST_MIME_TYPES:
                raise HTTPUnsupportedMediaType()

        elif mimetype:
            if mimetype not in SUPPORTED_TEXT_MIME_TYPES:
                raise HTTPUnsupportedMediaType()

            message.mimetype = mimetype

        else:
            message.mimetype = 'text/plain'

        DBSession.add(message)
        DBSession.flush()
        queues.push(settings.messaging.workers_queue, message.to_dict())
        return message

    @authorize
    @store_manager(DBSession)
    @json
    @commit
    def see(self, id):
        id = int_or_notfound(id)
        member = Member.current()

        message = DBSession.query(Message).get(id)
        if message is None:
            raise HTTPNotFound()

        if message.sender_id == member.id:
            raise HTTPStatus('621 Can Not See Own Message')

        member_message_seen = DBSession.query(MemberMessageSeen) \
            .filter(MemberMessageSeen.member_id == member.id) \
            .filter(MemberMessageSeen.message_id == message.id) \
            .one_or_none()

        if member_message_seen is not None:
            raise HTTPStatus('619 Message Already Seen')

        query = DBSession.query(Message) \
            .filter(Message.target_id == message.target_id) \
            .filter(Message.created_at <= message.created_at) \
            .filter(Message.seen_at == None) \
            .filter(Message.sender_id != member.id) \

        query = Message.filter_by_request(query)

        for m in query:
            m.seen_by.append(member)

        seen_message = message.to_dict()
        seen_message.update({'type': 'seen'})
        queues.push(settings.messaging.workers_queue, seen_message)
        return message

