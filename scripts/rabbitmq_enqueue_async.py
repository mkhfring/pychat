#! /usr/bin/env python3.6

import json
import asyncio
import argparse
import functools

import aio_pika


DEFAULT_MESSAGE = '''{
    "id": 1,
    "body": "Sample Message"
}'''


parser = argparse.ArgumentParser()
parser.add_argument(
    'session_id',
    help='Session id',
)
parser.add_argument(
    'target_id',
    help='Target id',
)
parser.add_argument(
    'payload',
    help='A JSON-like string. Default: %s' % DEFAULT_MESSAGE.replace('\n', ' '),
    default=DEFAULT_MESSAGE,
    nargs='?'
)



async def main(loop):
    args = parser.parse_args()

    connection = await aio_pika.connect_robust(
        'amqp://guest:guest@127.0.0.1/',
        loop=loop
    )

    async with connection:
        # The routing_key must be the same as the `queue` parameter in
        # `jaguar route start <queue>`
        routing_key = 'workers'
        channel = await connection.channel()
        payload = json.loads(args.payload)
        payload['sessionId'] = args.session_id
        payload['targetId'] = args.target_id
        payload = json.dumps(payload)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=payload.encode()
            ),
            routing_key=routing_key
        )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

