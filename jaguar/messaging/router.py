import asyncio

import ujson
from restfulpy.orm import DBSession

from . import queues, sessions
from jaguar import asyncdb
from jaguar.models import TargetMember, Member


async def route(envelop):
    if envelop.get('type') == 'seen':
        await dispatch(envelop, envelop['senderId'])

    elif envelop.get('type') == 'mention':
        await dispatch(envelop, envelop['mentionedMember'])

    else:
        members = await asyncdb.get_members_by_target(envelop['targetId'])
        for member in members:
            member_id = member.get('id')
            await dispatch(envelop, member_id)


async def start(name):
    print('Message router started')
    while True:
        queue, message = await queues.bpop_async(name)
        print(f'Processing message: {message}')
        await route(ujson.loads(message))


async def dispatch(envelop, member_id):
    active_sessions = await sessions.get_sessions(member_id)
    for session, queue in active_sessions.items():
        envelop['isMine'] = member_id == envelop['senderId']
        envelop['sessionId'] = session.decode()
        await queues.push_async(queue, envelop)

