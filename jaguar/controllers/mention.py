from sqlalchemy.orm import aliased
from nanohttp import json, context, settings, HTTPNotFound, HTTPStatus
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..messaging import queues
from ..models import Mention, Member, Direct, TargetMember, Target
from ..validators import mention_validator
from ..webhooks import Webhook
from ..exceptions import HTTPTargetNotFound


class MentionController(ModelRestController):
    __model__ = Mention

    def __init__(self, target=None, member=None):
        self.target = target
        self.member = member

    @authorize
    @mention_validator
    @json
    @commit
    def mention(self):
        form = context.form
        mention = Mention()
        mention.body = form.get('body')

        origin_target = DBSession.query(Target) \
            .filter(Target.id == form.get('originTargetId')) \
            .one_or_none()
        if origin_target is None:
            raise HTTPTargetNotFound()

        mention.origin_target_id = origin_target.id

        if not (self.target or self.member):
            raise HTTPNotFound()

        if self.target:
            mention.target_id = self.target.id
            mention.sender_id = Member.current().id
            DBSession.add(mention)
            DBSession.flush()
            queues.push(settings.messaging.workers_queue, mention.to_dict())

        else:
            mentioner = Member.current()
            mentioned = self.member

            if mentioner.id == mentioned.id:
                raise HTTPStatus('620 Can Not Mention Yourself')

            aliased_target = aliased(Target)
            aliased_target_member1 = aliased(TargetMember)
            aliased_target_member2 = aliased(TargetMember)

            target_member = DBSession.query(aliased_target_member1) \
                .join(
                    aliased_target_member2,
                    aliased_target_member2.target_id == \
                    aliased_target_member1.target_id
                ) \
                .filter(aliased_target_member2.member_id == mentioner.id) \
                .filter(aliased_target_member1.member_id == mentioned.id) \
                .join(
                    aliased_target,
                    aliased_target.id == aliased_target_member1.target_id
                ) \
                .filter(aliased_target.type == 'direct') \
                .one_or_none()

            mention.sender_id = mentioner.id
            if target_member is None:
                direct = Direct(members=[mentioner, mentioned])
                DBSession.add(direct)
                DBSession.flush()
                mention.target_id = direct.id

            else:
                mention.target_id = target_member.target_id

            DBSession.add(mention)
            DBSession.flush()
            mention_message = mention.to_dict()
            mention_message.update(
                {'mentionedMember': mentioned.id, 'type': 'mention'}
            )
            queues.push(settings.messaging.workers_queue, mention_message)
            webhook = Webhook()
            webhook.mentioned_member(
                mention.origin_target_id,
                mentioned.reference_id
            )

        return mention

