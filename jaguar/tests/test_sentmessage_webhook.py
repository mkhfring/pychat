from nanohttp import settings

from jaguar.tests.helpers import thirdparty_mockup_server, \
    AutoDocumentationBDDTest
from jaguar.webhooks import Webhook


class TestSentWebhook(AutoDocumentationBDDTest):

    def test_webhook_sent_message(self):
        webhook = Webhook()

        with thirdparty_mockup_server():
            # No raise
            assert webhook.sent_message(1, 1) is None

            # When thirdparty response with status != HTTPNoContent
            assert webhook.sent_message('bad', 'bad') is None

            # When a request error occurs
            settings.merge(f'''
              webhooks:
                sent:
                  url: invalid-url
            ''')
            assert webhook.sent_message(1, 1) is None

