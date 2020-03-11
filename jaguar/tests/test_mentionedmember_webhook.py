from nanohttp import settings

from jaguar.tests.helpers import thirdparty_mockup_server, \
    AutoDocumentationBDDTest
from jaguar.webhooks import Webhook


class TestMentionedWebhook(AutoDocumentationBDDTest):

    def test_webhook_mentioned_message(self):
        webhook = Webhook()

        with thirdparty_mockup_server():
            # No raise
            assert webhook.mentioned_member(
                room_id=1,
                mentioned_reference_id=1
            ) is None

            # When thirdparty response with status != HTTPNoContent
            assert webhook.mentioned_member(
                room_id='bad',
                mentioned_reference_id='bad'
            ) is None

            # When a request error occur
            settings.merge(f'''
              webhooks:
                mentioned:
                  url: invalid-url
            ''')
            assert webhook.mentioned_member(
                room_id=1,
                mentioned_reference_id=1
            ) is None

